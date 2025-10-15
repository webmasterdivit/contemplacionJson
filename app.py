#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Aplicación para generar contemplaciones litúrgicas en formato JSON
Obtiene entradas desde el API de WordPress de diegojavier.wordpress.com
"""

import json
import os
import re
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass
from pathlib import Path
from bs4 import BeautifulSoup
import time


@dataclass
class Contemplacion:
    """Clase que representa una contemplación litúrgica"""
    id: int  # ID numérico de WordPress
    ciclo: str  # A, B, C
    tiempo_liturgico: str
    titulo: str
    lecturas: str
    resumen: str
    link: str  # URL del post original
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "ciclo": self.ciclo,
            "tiempo_liturgico": self.tiempo_liturgico,
            "titulo": self.titulo,
            "lecturas": self.lecturas,
            "resumen": self.resumen,
            "link": self.link
        }


class WordPressAPI:
    """Cliente para interactuar con el API de WordPress"""
    
    def __init__(self, base_url: str = "https://diegojavier.wordpress.com"):
        self.base_url = base_url.rstrip('/')
        self.api_url = f"{self.base_url}/wp-json/wp/v2"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ContemplacionesLiturgicas/1.0'
        })
    
    def obtener_posts(self, per_page=10, max_posts=50):
        """Obtiene posts desde WordPress usando el API REST"""
        posts = []
        
        # Probar diferentes endpoints del API de WordPress
        endpoints_a_probar = [
            f"{self.base_url}/wp-json/wp/v2/posts",
            f"{self.base_url}/?rest_route=/wp/v2/posts",
            f"{self.base_url}/index.php?rest_route=/wp/v2/posts"
        ]
        
        for endpoint in endpoints_a_probar:
            print(f"Probando endpoint: {endpoint}")
            try:
                response = requests.get(endpoint, timeout=30)
                if response.status_code == 200:
                    # Verificar si realmente es JSON válido
                    try:
                        test_json = response.json()
                        print(f"✓ Endpoint funciona: {endpoint}")
                        break
                    except json.JSONDecodeError:
                        print(f"✗ Endpoint responde pero no es JSON válido: {endpoint}")
                        continue
                else:
                    print(f"✗ Endpoint falló ({response.status_code}): {endpoint}")
            except Exception as e:
                print(f"✗ Error en endpoint {endpoint}: {e}")
        else:
            # Si ningún endpoint funciona, intentar scraping básico
            print("Ningún API de WordPress disponible, intentando scraping básico...")
            return self._scrape_posts_basico()
        
        page = 1
        while len(posts) < max_posts:
            params = {
                'page': page,
                'per_page': per_page,
                'status': 'publish',
                '_embed': True
            }
            
            print(f"Página {page}: {endpoint}")
            
            try:
                response = requests.get(endpoint, params=params, timeout=30)
                
                if response.status_code == 404:
                    print(f"No hay más páginas (404)")
                    break
                
                response.raise_for_status()
                page_posts = response.json()
                
                if not page_posts:
                    print(f"No hay más posts en la página {page}")
                    break
                
                posts.extend(page_posts)
                print(f"✓ Obtenidos {len(page_posts)} posts de la página {page}")
                
                page += 1
                
            except requests.exceptions.RequestException as e:
                print(f"Error al obtener posts de la página {page}: {e}")
                break
        
        return posts[:max_posts]
    
    def _scrape_posts_basico(self):
        """Método de fallback para obtener posts mediante scraping básico"""
        print("Intentando obtener posts mediante scraping...")
        
        all_post_urls = set()
        
        try:
            # Scraping de múltiples páginas y archivos
            pages_to_scrape = [
                f"{self.base_url}",  # Página principal
                f"{self.base_url}/page/2/",  # Página 2
                f"{self.base_url}/page/3/",  # Página 3
                f"{self.base_url}/page/4/",  # Página 4
                f"{self.base_url}/page/5/",  # Página 5
                # Archivos por año
                f"{self.base_url}/2024/",
                f"{self.base_url}/2023/", 
                f"{self.base_url}/2022/",
                f"{self.base_url}/2021/",
                f"{self.base_url}/2020/",
                # Sitemap de WordPress
                f"{self.base_url}/sitemap.xml",
                f"{self.base_url}/wp-sitemap.xml",
            ]
            
            print(f"Escaneando {len(pages_to_scrape)} páginas del blog...")
            
            for page_num, page_url in enumerate(pages_to_scrape, 1):
                try:
                    print(f"Escaneando página {page_num}: {page_url}")
                    response = requests.get(page_url, timeout=30)
                    
                    if response.status_code == 404:
                        print(f"✗ Página {page_num} no existe (404)")
                        continue
                        
                    response.raise_for_status()
                    content = response.text
                    
                    # Detectar si es XML (sitemap)
                    if page_url.endswith('.xml') and 'xml' in content[:100].lower():
                        print(f"  📄 Procesando sitemap XML...")
                        # Patrón para URLs en sitemaps XML
                        xml_pattern = r'<loc>(https://diegojavier\.wordpress\.com/\d{4}/\d{2}/\d{2}/[^<]+)</loc>'
                        page_urls = re.findall(xml_pattern, content)
                    else:
                        # Patrones para encontrar URLs de posts individuales en HTML
                        patterns = [
                            r'https://diegojavier\.wordpress\.com/\d{4}/\d{2}/\d{2}/[^/\s"\']+/?',
                            r'href="(https://diegojavier\.wordpress\.com/\d{4}/\d{2}/\d{2}/[^/"]+/?)"',
                            r'"(https://diegojavier\.wordpress\.com/\d{4}/\d{2}/\d{2}/[^/"]+/?)"',
                            # Patrones adicionales para archivos WordPress
                            r'<a[^>]+href="(https://diegojavier\.wordpress\.com/\d{4}/\d{2}/\d{2}/[^"]+)"',
                        ]
                        
                        page_urls = []
                        for pattern in patterns:
                            matches = re.findall(pattern, content)
                            page_urls.extend(matches)
                    
                    # Limpiar URLs (remover fragmentos y parámetros)
                    cleaned_urls = []
                    for url in page_urls:
                        # Remover fragmentos (#) y parámetros (?)
                        clean_url = url.split('#')[0].split('?')[0].rstrip('/')
                        if clean_url and clean_url not in cleaned_urls:
                            cleaned_urls.append(clean_url)
                    
                    before_count = len(all_post_urls)
                    all_post_urls.update(cleaned_urls)
                    new_urls = len(all_post_urls) - before_count
                    
                    print(f"✓ Página {page_num}: {new_urls} URLs nuevas encontradas ({len(cleaned_urls)} URLs procesadas)")
                    
                except Exception as e:
                    print(f"✗ Error en página {page_num}: {e}")
                    continue
            
            # Convertir a lista y ordenar por fecha (más recientes primero)
            post_urls = sorted(list(all_post_urls), reverse=True)  # Procesar TODAS las URLs
            
            print(f"\n📊 Total de URLs únicas encontradas: {len(post_urls)}")
            print(f"🔄 Procesando TODAS las URLs con delay de 1.5 segundos entre peticiones...")
            
            if not post_urls:
                print("No se encontraron URLs de posts")
                return []
            
            posts = []
            failed_urls = []
            
            for i, url in enumerate(post_urls, 1):
                print(f"Procesando post {i}/{len(post_urls)}: {url}")
                
                try:
                    # Scraper individual del post
                    post_data = self._scrape_post_individual(url)
                    if post_data:
                        posts.append(post_data)
                        print(f"  ✓ Post procesado exitosamente")
                    else:
                        failed_urls.append(url)
                        print(f"  ✗ No se pudo extraer datos del post")
                        
                except Exception as e:
                    failed_urls.append(url)
                    print(f"  ✗ Error procesando post: {e}")
                    
                # Delay más largo para evitar bloqueos
                time.sleep(1.5)
                
                # Mostrar progreso cada 25 posts
                if i % 25 == 0:
                    print(f"\n📈 Progreso: {i}/{len(post_urls)} posts procesados ({len(posts)} exitosos, {len(failed_urls)} fallidos)")
            
            # Guardar URLs fallidas en un log
            self._save_failed_urls_log(failed_urls)
            
            print(f"✓ Obtenidos {len(posts)} posts exitosos mediante scraping")
            return posts
            
        except Exception as e:
            print(f"Error en scraping básico: {e}")
            return []
    
    def _save_failed_urls_log(self, failed_urls):
        """Guarda las URLs que no se pudieron procesar en un archivo de log"""
        if not failed_urls:
            print("\n✅ Todas las URLs se procesaron exitosamente!")
            return
            
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_filename = f"failed_urls_{timestamp}.log"
        
        try:
            with open(log_filename, 'w', encoding='utf-8') as f:
                f.write(f"# URLs que no se pudieron procesar - {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Total de URLs fallidas: {len(failed_urls)}\n\n")
                
                for i, url in enumerate(failed_urls, 1):
                    f.write(f"{i}. {url}\n")
                    
            print(f"\n📋 Log de URLs fallidas guardado en: {log_filename}")
            print(f"   Total de URLs fallidas: {len(failed_urls)}")
            
        except Exception as e:
            print(f"\n⚠️  Error al guardar log de URLs fallidas: {e}")
            print("URLs fallidas:")
            for i, url in enumerate(failed_urls, 1):
                print(f"  {i}. {url}")
    
    def _load_failed_urls_from_log(self, log_filename):
        """Carga URLs fallidas desde un archivo de log anterior"""
        try:
            with open(log_filename, 'r', encoding='utf-8') as f:
                urls = []
                for line in f:
                    line = line.strip()
                    # Ignorar comentarios y líneas vacías
                    if line and not line.startswith('#'):
                        # Extraer URL si tiene numeración
                        if '. http' in line:
                            url = line.split('. ', 1)[1]
                            urls.append(url)
                        elif line.startswith('http'):
                            urls.append(line)
                            
                print(f"📋 Cargadas {len(urls)} URLs fallidas desde {log_filename}")
                return urls
                
        except FileNotFoundError:
            print(f"⚠️  Archivo de log no encontrado: {log_filename}")
            return []
        except Exception as e:
            print(f"⚠️  Error al cargar log de URLs fallidas: {e}")
            return []
    
    def _scrape_post_individual(self, url):
        """Scraper para obtener datos de un post individual"""
        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer ID del post de la URL
            url_parts = url.strip('/').split('/')
            date_part = f"{url_parts[-4]}{url_parts[-3]}{url_parts[-2]}"  # YYYYMMDD
            slug_part = url_parts[-1]
            post_id = abs(hash(f"{date_part}{slug_part}")) % 100000  # ID basado en fecha y slug
            
            # Extraer título
            title_elem = soup.find('h1', class_='entry-title') or soup.find('h1') or soup.find('title')
            title = title_elem.get_text(strip=True) if title_elem else "Sin título"
            
            # Extraer contenido principal
            content_elem = (soup.find('div', class_='entry-content') or 
                          soup.find('div', class_='post-content') or 
                          soup.find('article') or 
                          soup.find('main'))
            
            content = ""
            if content_elem:
                # Buscar específicamente texto después de "Contemplación"
                contemplacion_text = ""
                all_text = content_elem.get_text(separator=' ', strip=True)
                
                # Buscar el patrón de contemplación
                if 'contemplación' in all_text.lower():
                    parts = re.split(r'contemplaci[óo]n', all_text, flags=re.IGNORECASE)
                    if len(parts) > 1:
                        contemplacion_text = parts[1].strip()[:200]
                
                if not contemplacion_text:
                    # Fallback: tomar los primeros 200 caracteres del contenido
                    contemplacion_text = all_text[:200]
                
                content = contemplacion_text
            
            if not content:
                content = "Contenido no disponible via scraping."
            
            # Buscar lecturas (patrones como "Jn 16, 12-15", "Lc 10, 1-12")
            lecturas = ""
            lectura_patterns = [
                r'[A-Za-z]{1,3}\s+\d{1,3},\s*\d{1,3}(?:-\d{1,3})?',
                r'[A-Za-z]{1,3}\s+\d{1,3}\.\s*\d{1,3}(?:-\d{1,3})?',
            ]
            
            full_text = soup.get_text()
            for pattern in lectura_patterns:
                matches = re.findall(pattern, full_text)
                if matches:
                    lecturas = '; '.join(matches[:3])  # Tomar máximo 3 lecturas
                    break
            
            return {
                'id': post_id,
                'link': url,
                'title': {'rendered': title},
                'excerpt': {'rendered': content[:200] + '...' if len(content) > 200 else content},
                'content': {'rendered': content},
                'lecturas': lecturas  # Campo extra para las lecturas encontradas
            }
            
        except Exception as e:
            print(f"Error scraping post individual {url}: {e}")
            return None
    
    def limpiar_contenido_html(self, html_content: str) -> str:
        """Limpia el contenido HTML y extrae solo el texto"""
        if not html_content:
            return ""
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remover scripts y estilos
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Obtener texto limpio
        text = soup.get_text()
        
        # Limpiar espacios en blanco excesivos
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text


class ProcesadorContemplaciones:
    """Procesador de contemplaciones litúrgicas"""
    
    TIEMPOS_LITURGICOS = [
        "Adviento",
        "Navidad", 
        "Cuaresma",
        "Pascua",
        "Tiempo Ordinario"
    ]
    
    CICLOS = ["A", "B", "C"]
    
    def __init__(self, wordpress_url: str = "https://diegojavier.wordpress.com"):
        self.wordpress_api = WordPressAPI(wordpress_url)
        self.contemplaciones = []
    
    def validar_ciclo(self, ciclo: str) -> bool:
        """Valida que el ciclo sea A, B o C"""
        return ciclo.upper() in self.CICLOS
    
    def validar_tiempo_liturgico(self, tiempo: str) -> bool:
        """Valida que el tiempo litúrgico sea válido"""
        return tiempo in self.TIEMPOS_LITURGICOS
    
    def extraer_lecturas(self, texto: str) -> str:
        """Extrae las referencias de lecturas del texto"""
        # Busca patrones como "Mt 5, 1-12", "Jn 16, 12-15", etc.
        patron_lectura = r'([A-Za-z]{1,4})\s+(\d+),?\s*(\d+(?:-\d+)?)'
        lecturas = re.findall(patron_lectura, texto)
        
        if lecturas:
            # Convierte las tuplas en formato estándar
            lecturas_formateadas = []
            for libro, capitulo, versiculo in lecturas:
                lecturas_formateadas.append(f"{libro} {capitulo}, {versiculo}")
            return "; ".join(lecturas_formateadas)
        
        return ""
    
    def determinar_tiempo_liturgico(self, titulo: str, contenido: str) -> str:
        """Determina el tiempo litúrgico basado en el contenido"""
        texto_completo = (titulo + " " + contenido).lower()
        
        # Patrones para identificar tiempos litúrgicos
        patrones = {
            "Adviento": ["adviento", "preparación navidad", "espera", "venida del señor"],
            "Navidad": ["navidad", "nacimiento", "belén", "pesebre", "nochebuena"],
            "Cuaresma": ["cuaresma", "miércoles de ceniza", "ayuno", "penitencia", "desierto"],
            "Pascua": ["pascua", "resurrección", "aleluya", "pentecostés", "semana santa", "triduo"],
            "Tiempo Ordinario": ["tiempo ordinario", "domingo", "vida de jesús"]
        }
        
        for tiempo, palabras_clave in patrones.items():
            if any(palabra in texto_completo for palabra in palabras_clave):
                return tiempo
        
        return "Tiempo Ordinario"  # Por defecto
    
    def determinar_ciclo(self, lecturas: str) -> str:
        """Determina el ciclo litúrgico basado en las lecturas"""
        if not lecturas:
            return "A"  # Por defecto
        
        # Patrones para evangelistas
        if any(libro in lecturas for libro in ["Mt", "Mateo"]):
            return "A"
        elif any(libro in lecturas for libro in ["Mc", "Marcos"]):
            return "B"
        elif any(libro in lecturas for libro in ["Lc", "Lucas"]):
            return "C"
        elif any(libro in lecturas for libro in ["Jn", "Juan"]):
            # Juan se usa en todos los ciclos, especialmente en Pascua
            return "A"  # Por defecto
        
        return "A"  # Por defecto
    
    def procesar_post_wordpress(self, post: Dict) -> Contemplacion:
        """Procesa un post de WordPress y crea una contemplación"""
        
        # Extraer datos básicos del post
        post_id = post.get('id', 0)
        titulo = self.wordpress_api.limpiar_contenido_html(post.get('title', {}).get('rendered', ''))
        contenido_html = post.get('content', {}).get('rendered', '')
        contenido = self.wordpress_api.limpiar_contenido_html(contenido_html)
        
        # Extraer lecturas - primero del campo de scraping, luego del contenido
        lecturas = post.get('lecturas', '') or self.extraer_lecturas(contenido)
        
        # Determinar tiempo litúrgico
        tiempo_liturgico = self.determinar_tiempo_liturgico(titulo, contenido)
        
        # Determinar ciclo
        ciclo = self.determinar_ciclo(lecturas)
        
        # Extraer resumen (primeros 200 caracteres después de "Contemplación")
        resumen = ""
        contenido_lower = contenido.lower()
        
        # Buscar diferentes variaciones de "contemplación"
        patrones_contemplacion = ["contemplación", "contemplacion", "contemplamos", "contempla"]
        
        idx_contemplacion = -1
        for patron in patrones_contemplacion:
            idx = contenido_lower.find(patron)
            if idx != -1:
                idx_contemplacion = idx + len(patron)
                break
        
        if idx_contemplacion != -1:
            resumen = contenido[idx_contemplacion:idx_contemplacion + 200].strip()
        else:
            # Si no encuentra "contemplación", toma los primeros 200 caracteres
            resumen = contenido[:200].strip()
        
        # Obtener el link del post
        link = post.get('link', '') or post.get('guid', {}).get('rendered', '')
        
        return Contemplacion(
            id=post_id,
            ciclo=ciclo,
            tiempo_liturgico=tiempo_liturgico,
            titulo=titulo,
            lecturas=lecturas,
            resumen=resumen,
            link=link
        )
    
    def cargar_desde_wordpress(self, max_posts: int = 100):
        """Carga contemplaciones desde WordPress"""
        print("Conectando con el API de WordPress...")
        
        try:
            # Obtener posts desde WordPress
            posts = self.wordpress_api.obtener_posts(per_page=50, max_posts=max_posts)
            
            if not posts:
                print("No se encontraron posts en WordPress")
                return
            
            print(f"Procesando {len(posts)} posts...")
            
            # Procesar cada post
            for i, post in enumerate(posts[:max_posts], 1):
                try:
                    contemplacion = self.procesar_post_wordpress(post)
                    self.contemplaciones.append(contemplacion)
                    
                    if i % 10 == 0:
                        print(f"Procesados {i}/{len(posts)} posts...")
                        
                except Exception as e:
                    print(f"Error procesando post {post.get('id', 'desconocido')}: {e}")
                    continue
            
            print(f"Carga completada: {len(self.contemplaciones)} contemplaciones procesadas")
            
        except Exception as e:
            print(f"Error al cargar desde WordPress: {e}")
            raise
    
    def generar_json(self, archivo_salida: str = "salida/contemplaciones.json"):
        """Genera el archivo JSON con las contemplaciones"""
        
        # Crear directorio de salida si no existe
        Path(archivo_salida).parent.mkdir(parents=True, exist_ok=True)
        
        # Convertir contemplaciones a diccionarios
        datos_json = [contemplacion.to_dict() for contemplacion in self.contemplaciones]
        
        # Escribir archivo JSON
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            json.dump(datos_json, f, ensure_ascii=False, indent=2)
        
        print(f"Archivo generado: {archivo_salida}")
        print(f"Total de contemplaciones: {len(self.contemplaciones)}")
    
    def mostrar_estadisticas(self):
        """Muestra estadísticas de las contemplaciones procesadas"""
        if not self.contemplaciones:
            print("No hay contemplaciones para mostrar estadísticas")
            return
        
        # Contar por tiempo litúrgico
        tiempos = {}
        ciclos = {}
        
        for contemplacion in self.contemplaciones:
            tiempos[contemplacion.tiempo_liturgico] = tiempos.get(contemplacion.tiempo_liturgico, 0) + 1
            ciclos[contemplacion.ciclo] = ciclos.get(contemplacion.ciclo, 0) + 1
        
        print("\n=== ESTADÍSTICAS ===")
        print(f"Total de contemplaciones: {len(self.contemplaciones)}")
        print("\nPor tiempo litúrgico:")
        for tiempo, cantidad in tiempos.items():
            print(f"  {tiempo}: {cantidad}")
        
        print("\nPor ciclo:")
        for ciclo, cantidad in ciclos.items():
            print(f"  Ciclo {ciclo}: {cantidad}")


def main():
    """Función principal"""
    print("=== GENERADOR DE CONTEMPLACIONES LITÚRGICAS ===")
    print("Obteniendo entradas desde https://diegojavier.wordpress.com/\n")
    
    try:
        # Crear procesador
        procesador = ProcesadorContemplaciones("https://diegojavier.wordpress.com")
        
        # Cargar datos desde WordPress
        print("Conectando con WordPress...")
        procesador.cargar_desde_wordpress(max_posts=200)
        
        if not procesador.contemplaciones:
            print("No se pudieron obtener contemplaciones. Proceso terminado.")
            return
        
        # Mostrar estadísticas
        procesador.mostrar_estadisticas()
        
        # Generar archivo JSON
        print("\nGenerando archivo JSON...")
        procesador.generar_json()
        
        print("\n¡Proceso completado exitosamente!")
        print(f"Archivo generado: salida/contemplaciones.json")
        
    except Exception as e:
        print(f"\nError durante el proceso: {e}")
        print("Por favor, verifica la conexión a internet y que el sitio esté disponible.")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())