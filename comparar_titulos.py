#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para comparar títulos entre contemplaciones.json y fuente_agente.json
y obtener los links correspondientes
"""

import json
import re
from difflib import SequenceMatcher
from typing import Dict, List, Tuple, Optional

def cargar_json(ruta_archivo: str) -> List[Dict]:
    """Carga un archivo JSON y retorna su contenido"""
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def normalizar_texto(texto: str) -> str:
    """Normaliza un texto para comparación: quita acentos, espacios extra, etc."""
    # Convertir a minúsculas
    texto = texto.lower()
    
    # Reemplazar caracteres especiales y acentos
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u', 'ñ': 'n',
        'à': 'a', 'è': 'e', 'ì': 'i', 'ò': 'o', 'ù': 'u',
        'â': 'a', 'ê': 'e', 'î': 'i', 'ô': 'o', 'û': 'u',
        'ä': 'a', 'ë': 'e', 'ï': 'i', 'ö': 'o', 'ü': 'u',
        'ç': 'c', '«': '"', '»': '"', '"': '"', '"': '"',
        ''': "'", ''': "'", '–': '-', '—': '-'
    }
    
    for old, new in replacements.items():
        texto = texto.replace(old, new)
    
    # Quitar caracteres especiales y normalizar espacios
    texto = re.sub(r'[^\w\s-]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto)
    texto = texto.strip()
    
    return texto

def extraer_palabras_clave(titulo: str) -> List[str]:
    """Extrae palabras clave de un título, excluyendo palabras comunes"""
    palabras_comunes = {
        'el', 'la', 'los', 'las', 'un', 'una', 'y', 'o', 'de', 'del', 'al', 
        'en', 'con', 'por', 'para', 'que', 'es', 'se', 'a', 'e', 'i', 'o', 'u',
        'domingo', 'b', 'c', 'a', 'cuaresma', 'pascua', 'adviento', 'navidad'
    }
    
    texto_norm = normalizar_texto(titulo)
    palabras = [p for p in texto_norm.split() if len(p) > 2 and p not in palabras_comunes]
    return palabras

def calcular_similitud(titulo1: str, titulo2: str) -> float:
    """Calcula la similitud entre dos títulos usando diferentes métodos"""
    # Normalizar ambos títulos
    norm1 = normalizar_texto(titulo1)
    norm2 = normalizar_texto(titulo2)
    
    # Similitud de secuencia básica
    similitud_basica = SequenceMatcher(None, norm1, norm2).ratio()
    
    # Similitud por palabras clave
    palabras1 = set(extraer_palabras_clave(titulo1))
    palabras2 = set(extraer_palabras_clave(titulo2))
    
    if len(palabras1) == 0 or len(palabras2) == 0:
        similitud_palabras = 0.0
    else:
        intersection = len(palabras1.intersection(palabras2))
        union = len(palabras1.union(palabras2))
        similitud_palabras = intersection / union if union > 0 else 0.0
    
    # Promedio ponderado
    similitud_final = (similitud_basica * 0.4) + (similitud_palabras * 0.6)
    
    return similitud_final

def buscar_mejor_coincidencia(titulo_contemplacion: str, fuente_agente: List[Dict], umbral: float = 0.3) -> Optional[Tuple[Dict, float]]:
    """Busca la mejor coincidencia para un título de contemplación en fuente_agente"""
    mejor_coincidencia = None
    mejor_similitud = 0.0
    
    for entrada in fuente_agente:
        title_fuente = entrada.get('title', '')
        file_fuente = entrada.get('file', '')
        
        # Solo considerar entradas que son contemplaciones
        if not file_fuente.startswith('contemplaciones -'):
            continue
            
        similitud = calcular_similitud(titulo_contemplacion, title_fuente)
        
        if similitud > mejor_similitud and similitud >= umbral:
            mejor_similitud = similitud
            mejor_coincidencia = (entrada, similitud)
    
    return mejor_coincidencia

def main():
    """Función principal"""
    # Rutas de archivos
    ruta_contemplaciones = '/home/lucas/divit/contemplacionJson/salida/contemplaciones.json'
    ruta_fuente_agente = '/home/lucas/divit/contemplacionJson/salida/fuente_agente.json'
    
    try:
        print("Cargando archivos...")
        
        # Cargar datos
        contemplaciones = cargar_json(ruta_contemplaciones)
        fuente_agente = cargar_json(ruta_fuente_agente)
        
        print(f"- contemplaciones.json: {len(contemplaciones)} entradas")
        print(f"- fuente_agente.json: {len(fuente_agente)} entradas")
        
        # Filtrar solo contemplaciones en fuente_agente
        contemplaciones_fuente = [
            entrada for entrada in fuente_agente 
            if entrada.get('file', '').startswith('contemplaciones -')
        ]
        print(f"- Contemplaciones en fuente_agente: {len(contemplaciones_fuente)}")
        
        print("\n=== COMPARACIÓN DE TÍTULOS ===")
        print("Formato: [Similitud%] Título contemplacion -> Título fuente_agente")
        print("Link: [URL]")
        print("-" * 80)
        
        coincidencias_encontradas = 0
        sin_coincidencias = 0
        
        for contemplacion in contemplaciones:
            titulo_cont = contemplacion.get('titulo', '')
            if not titulo_cont:
                continue
            
            resultado = buscar_mejor_coincidencia(titulo_cont, fuente_agente, umbral=0.2)
            
            if resultado:
                entrada_fuente, similitud = resultado
                print(f"[{similitud*100:.1f}%] {titulo_cont}")
                print(f"      -> {entrada_fuente.get('title', '')}")
                print(f"      Link: {entrada_fuente.get('link', 'N/A')}")
                print()
                coincidencias_encontradas += 1
            else:
                print(f"[0.0%] SIN COINCIDENCIA: {titulo_cont}")
                sin_coincidencias += 1
        
        print("-" * 80)
        print(f"RESUMEN:")
        print(f"- Coincidencias encontradas: {coincidencias_encontradas}")
        print(f"- Sin coincidencias: {sin_coincidencias}")
        print(f"- Total procesado: {len(contemplaciones)}")
        print(f"- Porcentaje de coincidencias: {(coincidencias_encontradas/len(contemplaciones)*100):.1f}%")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Archivo no encontrado - {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON inválido - {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()