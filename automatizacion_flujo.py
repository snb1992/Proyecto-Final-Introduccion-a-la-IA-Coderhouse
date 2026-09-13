import requests
import json
import csv
import datetime
import os

API_URL = "http://localhost:8000/api/optimize"
REGISTRY_FILE = "registro_analisis_sheets.csv"
EMAIL_OUTPUT_FILE = "email_enviado_gmail.html"

def paso_1_trigger_formulario():
    """
    Simula el 'Trigger' de Google Forms/Typeform.
    Devuelve los datos de una nueva respuesta.
    """
    print("1. [Trigger] Nueva respuesta detectada en el formulario web.")
    return {
        "email_solicitante": "usuario@ejemplo.com",
        "target_role": "Analista de Datos Jr.",
        "cv_text": "Estudiante avanzado de Cs. Económicas. Experiencia como encargado de caja en supermercado y ayudante administrativo en estudio contable. Habilidades: Excel, trabajo en equipo, responsable.",
        "job_description": ""
    }

def paso_2_y_3_procesamiento_ia(datos_formulario):
    """
    Simula los módulos HTTP/IA y Parse JSON de Make/Zapier.
    Llama a nuestra propia API y parsea la respuesta.
    """
    print("2/3. [Procesamiento IA] Enviando datos a la API de Claude (vía nuestro backend)...")
    payload = {
        "target_role": datos_formulario["target_role"],
        "cv_text": datos_formulario["cv_text"],
        "job_description": datos_formulario["job_description"]
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        json_data = response.json()
        print(f"   -> ¡Respuesta recibida y parseada correctamente! (Puntaje ATS: {json_data.get('ats_score')})")
        return json_data
    except requests.exceptions.ConnectionError:
        print("   -> ERROR: La API local no está corriendo. Ejecuta 'python cv_optimizer_api.py' primero.")
        exit(1)
    except Exception as e:
        print(f"   -> ERROR en la llamada a la IA: {e}")
        exit(1)

def paso_4_registro_sheets(datos_formulario, resultado_ia):
    """
    Simula el módulo Google Sheets -> 'Add a Row'.
    Guarda los metadatos para trazabilidad.
    """
    print("4. [Registro] Guardando trazabilidad en CSV (simulando Google Sheets)...")
    
    file_exists = os.path.isfile(REGISTRY_FILE)
    with open(REGISTRY_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Fecha", "Email", "Puesto Objetivo", "Puntaje ATS"])
        
        writer.writerow([
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            datos_formulario["email_solicitante"],
            datos_formulario["target_role"],
            resultado_ia.get("ats_score", "N/A")
        ])
    print(f"   -> Fila agregada en {REGISTRY_FILE}")

def paso_5_entrega_email(datos_formulario, resultado_ia):
    """
    Simula el módulo Gmail -> 'Send an Email'.
    Genera un archivo HTML estático simulando el correo recibido por el usuario.
    """
    print("5. [Entrega] Generando email de respuesta (simulando Gmail)...")
    
    # Construir la lista de experiencias mejoradas en HTML
    exp_html = ""
    for exp in resultado_ia.get("experience_items", []):
        exp_html += f"""
        <li style="margin-bottom: 15px;">
            <div style="color: #666; text-decoration: line-through; font-size: 0.9em;">Antes: {exp.get('original')}</div>
            <div style="font-weight: bold; color: #111;">Ahora: {exp.get('improved')}</div>
            <div style="color: #d32f2f; font-style: italic; font-size: 0.85em;">Nota del editor: {exp.get('editor_note')}</div>
        </li>
        """

    # Construir el HTML final del correo
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #1a73e8;">¡Tu CV ha sido optimizado con IA! 🚀</h2>
        <p>Hola, aquí tienes la primera revisión profesional de tu CV para el puesto de <strong>{datos_formulario['target_role']}</strong>.</p>
        
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0; border-left: 5px solid #34a853;">
            <h3 style="margin-top:0;">Puntaje de Compatibilidad ATS: {resultado_ia.get('ats_score')}/100</h3>
            <p><strong>Palabras clave faltantes:</strong> {", ".join(resultado_ia.get('missing_keywords', []))}</p>
        </div>

        <h3>Resumen Profesional Sugerido:</h3>
        <p style="background-color: #fff3e0; padding: 15px; border-radius: 4px;">{resultado_ia.get('summary_improved')}</p>

        <h3>Mejoras en tus Experiencias:</h3>
        <ul>
            {exp_html}
        </ul>

        <h3>Recomendaciones Adicionales:</h3>
        <ul>
            {"".join(f"<li>{r}</li>" for r in resultado_ia.get('recommendations', []))}
        </ul>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        <p style="font-size: 0.8em; color: #777;">Este es un mensaje automático del flujo simulado de Make/Zapier.</p>
    </body>
    </html>
    """

    with open(EMAIL_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"   -> Email generado exitosamente en {EMAIL_OUTPUT_FILE}")

def ejecutar_flujo_completo():
    print("=== INICIANDO FLUJO DE AUTOMATIZACIÓN (Make / Zapier Mock) ===\n")
    
    form_data = paso_1_trigger_formulario()
    ia_data = paso_2_y_3_procesamiento_ia(form_data)
    paso_4_registro_sheets(form_data, ia_data)
    paso_5_entrega_email(form_data, ia_data)
    
    print("\n=== FLUJO COMPLETADO CON ÉXITO ===")
    print("Revisa los archivos generados en este directorio.")

if __name__ == "__main__":
    ejecutar_flujo_completo()
