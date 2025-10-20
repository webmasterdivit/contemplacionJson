#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para actualizar los links en contemplaciones.json usando los datos de fuente_agente.json
"""

import json
import os
from typing import Dict, List, Optional

def cargar_json(ruta_archivo: str) -> List[Dict]:
    """Carga un archivo JSON y retorna su contenido"""
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        return json.load(f)

def guardar_json(ruta_archivo: str, datos: List[Dict]) -> None:
    """Guarda datos en un archivo JSON con formato legible"""
    with open(ruta_archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

def crear_indice_fuente(fuente_agente: List[Dict]) -> Dict[str, str]:
    """
    Crea un índice de títulos a links desde fuente_agente.json
    La clave será el título sin el prefijo "contemplaciones - "
    """
    indice = {}
    
    for entrada in fuente_agente:
        title = entrada.get('title', '')
        link = entrada.get('link', '')
        file = entrada.get('file', '')
        
        # Solo procesar entradas que tienen "contemplaciones -" en el archivo
        if file.startswith('contemplaciones - ') and title and link:
            # Remover el prefijo "contemplaciones - " del título para hacer la coincidencia
            # No es necesario porque el título ya viene sin el prefijo
            indice[title] = link
    
    return indice

def actualizar_links_contemplaciones(contemplaciones: List[Dict], indice_fuente: Dict[str, str]) -> int:
    """
    Actualiza los links en contemplaciones usando el índice de fuente_agente
    Retorna el número de actualizaciones realizadas
    """
    actualizaciones = 0
    
    for entrada in contemplaciones:
        titulo = entrada.get('titulo', '')
        link_actual = entrada.get('link', '')
        
        if titulo in indice_fuente:
            nuevo_link = indice_fuente[titulo]
            if link_actual != nuevo_link:
                entrada['link'] = nuevo_link
                actualizaciones += 1
                print(f"✓ Actualizado: '{titulo}' -> {nuevo_link}")
            else:
                print(f"= Sin cambios: '{titulo}' (ya tiene el link correcto)")
        else:
            print(f"⚠ No encontrado: '{titulo}' en fuente_agente")
    
    return actualizaciones

def main():
    """Función principal"""
    # Rutas de archivos
    ruta_contemplaciones = '/home/lucas/divit/contemplacionJson/salida/contemplaciones.json'
    ruta_fuente_agente = '/home/lucas/divit/contemplacionJson/salida/fuente_agente.json'
    ruta_backup = '/home/lucas/divit/contemplacionJson/salida/contemplaciones_backup.json'
    
    try:
        print("Cargando archivos...")
        
        # Cargar datos
        contemplaciones = cargar_json(ruta_contemplaciones)
        fuente_agente = cargar_json(ruta_fuente_agente)
        
        print(f"- contemplaciones.json: {len(contemplaciones)} entradas")
        print(f"- fuente_agente.json: {len(fuente_agente)} entradas")
        
        # Crear índice de fuente_agente
        print("\nCreando índice de fuente_agente...")
        indice_fuente = crear_indice_fuente(fuente_agente)
        print(f"- Índice creado con {len(indice_fuente)} entradas de contemplaciones")
        
        # Crear backup antes de modificar
        print(f"\nCreando backup en: {ruta_backup}")
        guardar_json(ruta_backup, contemplaciones)
        
        # Actualizar links
        print("\nActualizando links...")
        actualizaciones = actualizar_links_contemplaciones(contemplaciones, indice_fuente)
        
        # Guardar cambios
        if actualizaciones > 0:
            print(f"\nGuardando cambios... ({actualizaciones} actualizaciones)")
            guardar_json(ruta_contemplaciones, contemplaciones)
            print(f"✓ Archivo actualizado: {ruta_contemplaciones}")
        else:
            print("\n! No se realizaron actualizaciones")
        
        print(f"\n--- Proceso completado ---")
        print(f"Total de actualizaciones: {actualizaciones}")
        
    except FileNotFoundError as e:
        print(f"❌ Error: Archivo no encontrado - {e}")
    except json.JSONDecodeError as e:
        print(f"❌ Error: JSON inválido - {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == "__main__":
    main()