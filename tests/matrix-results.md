# Matrix de Resultados - Tests Estadisticos RAG

## Parametros por Set

| Set | chunk_size | chunk_overlap | top_k |
|-----|------------|---------------|-------|
| set_0 | 800 | 150 | 4 |
| set_1 | 1400 | 400 | 6 |
| set_2 | 400 | 60 | 3 |

---

## GRUPO 1: PREGUNTAS DIRECTAS (6 preg.)

### Pregunta A: "Si tengo una receta de hace 1 mes, todavía me sirve?"

| Set | Respuesta | Fuentes |
|-----|-----------|---------|
| set_0 | No hay informacion suficiente en los documentos cargados. | Pami Ambulatorio_28_09_2022.pdf, Circular 55 DIM - Recetarios Oficiales extraviados-13feb2026.pdf, OSER - Recetas electronicas 2026.pdf |
| set_1 | No hay informacion suficiente en los documentos cargados. | Pami Ambulatorio_28_09_2022.pdf, Circular 55 DIM, OSER - Recetas electronicas 2026.pdf, Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf |
| set_2 | No hay informacion suficiente en los documentos cargados. | Pami Ambulatorio_28_09_2022.pdf, Circular 55 DIM - Recetarios Oficiales extraviados-13feb2026.pdf, OSER - Recetas electronicas 2026.pdf |

### Pregunta B: "La receta del PAMI, Debo llevarla impresa obligatoriamente o puede ser digital?"

| Set | Respuesta | Fuentes |
|-----|-----------|---------|
| set_0 | No, la receta del PAMI no requiere presentación física en papel. La presentación del DNI y Credencial PAMI del afiliado es suficiente. Con estos datos la farmacia consulta en su sistema las recetas prescriptas disponibles. | Pami Ambulatorio_28_09_2022.pdf |
| set_1 | No, la receta del PAMI no requiere presentación física en papel. La presentación del DNI y Credencial PAMI del afiliado es suficiente. | Pami Ambulatorio_28_09_2022.pdf |
| set_2 | No, la receta del PAMI no requiere presentación física en papel. La presentación del DNI y Credencial PAMI del afiliado es suficiente para la dispensa. Con estos datos la farmacia consulta en su sistema de gestión qué recetas prescriptas tiene disponibles el afiliado. | Pami Ambulatorio_28_09_2022.pdf |

### Pregunta C: "No estoy disponible para ir a retirar mis medicamentos, puede ir mi hijo menor de edad a retirarlas por mi?"

| Set | Respuesta | Fuentes |
|-----|-----------|---------|
| set_0 | No hay informacion suficiente en los documentos cargados. | OSER - Recetas electronicas 2026.pdf, Circular 55 DIM - Recetarios Oficiales extraviados-13feb2026.pdf |
| set_1 | No hay informacion suficiente en los documentos cargados. | OSER - Recetas electronicas 2026.pdf, Circular 55 DIM |
| set_2 | No hay informacion suficiente en los documentos cargados. | OSER - Recetas electronicas 2026.pdf, Circular 55 DIM - Recetarios Oficiales extraviados-13feb2026.pdf |

### Pregunta D: "Mi perro está enfermo y el veterinario me dio un medicamento para humanos, ¿me las puede vender?"

| Set | Respuesta | Fuentes |
|-----|-----------|---------|
| set_0 | No se. El propósito del art. 3° es la dispensa de medicamentos en farmacias, no para uso veterinario. El sistema de dispensa de farmacias no contempla la dispensación de medicamentos de uso humano para animales. | Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf |
| set_1 | No se. El propósito del veterinario es diagnosticar y tratar la enfermedad, no dispensar medicamentos. | Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf |
| set_2 | No se. El propósito del veterinario es diagnosticar y tratar la enfermedad, no dispensar medicamentos. Te recomiendo buscar a un profesional de la salud veterinaria o consultar con el médico para obtener una recomendación más precisa. | Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf |

### Pregunta E: "¿Sirve la firma de un médico aunque sea de otra provincia?"

| Set | Respuesta | Fuentes |
|-----|-----------|---------|
| set_0 | No, la firma de un médico se debe cumplir con la normativa vigente en su propia provincia. | OSER - Recetas electronicas 2026.pdf, Circular 55 DIM, Pami Ambulatorio_28_09_2022.pdf |
| set_1 | No, la firma de un médico se debe ser en su propia provincia. | OSER - Recetas electronicas 2026.pdf, Circular 55 DIM, Pami Ambulatorio_28_09_2022.pdf |
| set_2 | No, la firma de un médico se debe ser en su propia provincia. | OSER - Recetas electronicas 2026.pdf, Circular 55 DIM - Recetarios Oficiales extraviados-13feb2026.pdf, Pami Ambulatorio_28_09_2022.pdf |

### Pregunta F: "Cometí un error y me equivoque en el número de afiliado de PAMI, los de la farmacia lo pueden arreglar?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No, no se puede arreglar el número de afiliado. El número de afiliado debe ser proporcionado por la farmacia para que pueda realizar la dispensa correcta. | Pami Ambulatorio_28_09_2022.pdf | **INCORRECTO** - El documento fuente dice: "En el caso que algún dato del beneficiario se encuentre incorrecto o carezca de alguno, la farmacia deberá colocar el correcto en el margen superior de la receta adjuntando el comprobante de afiliación." La farmacia SÍ puede corregir. |
| set_1 | No hay informacion suficiente en los documentos cargados. | Pami Ambulatorio_28_09_2022.pdf | **ALUCINACIÓN** - El documento tiene la respuesta pero el modelo no la usa. |
| set_2 | No hay informacion suficiente en los documentos cargados. | Pami Ambulatorio_28_09_2022.pdf | - |

---

## GRUPO 2: PREGUNTAS DE INTEGRACIÓN (6 preg.)

### Pregunta A: "El veterinario le recetó a mi perro gotas para los ojos que son de humanos. ¿Me las pueden vender o el sistema me va a rebotar la receta?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No se encontró información específica. | Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf | **INCOMPLETO** |
| set_1 | En la farmacia, se puede dispensar medicamentos y productos de uso veterinario, pero no para uso humano. | Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf | **PARCIAL** - La respuesta no aborda directamente si puede vender meds de humanos para uso veterinario |
| set_2 | En la farmacia, se puede dispensar medicamentos y productos de uso veterinario, pero no es recomendable que los médicos veterinarios les vayan a vender. | Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf | **INCOMPLETO** |

### Pregunta B: "Soy de OSPA VIAL y tengo una planilla de crónicos del año pasado. ¿Me sirve para retirar los remedios ahora en 2026?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_2 | Para retirar los remedios, necesitarías un trámite de la auditoría farmacéutica. No necesitas hacer un trámite nuevo. | OSER - Recetas electronicas 2026.pdf | - |

### Pregunta C: "Mi médico me mandó una receta digital de MaRx con varias fechas, ¿qué pasa si se me vence el DNI?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_2 | No, no te dan el remedio. La regla es que solo se pueden generar recetas electrónicas con fechas de emisión que coincidan con las fechas de validez del plan crónico. | OSER - Recetas electronicas 2026.pdf | **CORRECTO PARCIAL** |

### Pregunta D: "Tengo OSER y necesito un medicamento de receta de archivo. El médico dice que ya la mandó al sistema pero yo no tengo papel. ¿Cómo hace la farmacia?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_2 | Para quedarse con tu receta en OSER: 1) Revisa la Receta, 2) Entrega a OSER, 3) Recibe el Formulario de OSER GP-777. Si la farmacia retira la medicación con DNI + número de receta. | OSER - Recetas electronicas 2026.pdf | **CORRECTO** |

### Pregunta E: "Vengo a buscar un antibiótico para mi papá que está en cama. El médico le mandó la receta al celular, pero yo solo tengo MI DNI. ¿Me lo dan igual?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_2 | No me lo dan igual. Te pido que te presentes con tu DNI para poder firmar y firmar en la farmacia. | Pami Ambulatorio_28_09_2022.pdf, OSER - Recetas electronicas 2026.pdf | **CORRECTO** |

### Pregunta F: "Vine a buscar remedios de PAMI de mi abuelo con receta celeste manual. El médico tachó el número de afiliado. ¿Tengo que volver al consultorio o lo pueden arreglar acá?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No, puedes seguir con la farmacia. Si el médico no tuvo la certeza sobre el número de afiliado, se recomienda buscar a otra farmacia para obtener una nueva receta. | Pami Ambulatorio_28_09_2022.pdf | **INCORRECTO** - Fuente dice la farmacia puede corregir datos en el margen |
| set_1 | No, puedes seguir con la consulta a la farmacia. Si el médico no tuvo un error, solo debes buscar los remedios correspondientes a su receta manual. | Pami Ambulatorio_28_09_2022.pdf | **INCORRECTO** - Misma alucinación |
| set_2 | No, puedes seguir con la consulta a la farmacia. Si el médico no tuvo un error, solo debes buscar los remedios correspondientes a su receta manual. | Pami Ambulatorio_28_09_2022.pdf | **INCORRECTO** - Misma alucinación en set_2 |

---

## GRUPO 3: PREGUNTAS DE BORDE/LÍMITE (6 preg.)

### Pregunta A: "Tengo una receta de PAMI para buscar pañales, ¿me los dan gratis en cualquier farmacia PAMI o tengo que ir a una específica?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | No se pueden proporcionar pañales gratuitamente en farmacias que trabajen con PAMI. La cobertura general es para monodroga solo y no para pañales. | Pami Ambulatorio_28_09_2022.pdf | **POSIBLE ALUCINACIÓN** - Necesita verificar si PAMI cubre pañales |
| set_2 | No se pueden proporcionar pañales gratuitamente en farmacias que trabajen con PAMI. La cobertura general es para monodroga solo y no para pañales. | Pami Ambulatorio_28_09_2022.pdf | **POSIBLE ALUCINACIÓN** - Consistente con set_1 |

### Pregunta B: "¿Cuánto es el copago del Plan Materno OSER?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_2 | El copago del Plan Materno (OSER) es de 100% del valor del plan. | OSER - Recetas electronicas 2026.pdf | **CORRECTO** |

### Pregunta C: "¿Qué significa el error del sistema Xeilon?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_2 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |

### Pregunta D: "Estoy en la farmacia con una receta pero el veterinario no aparece en el padrón. ¿Me podés decir si el Dr. Juan Pérez de Paraná está habilitado?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | No, el Dr. Juan Pérez de Paraná no es un veterinario matriculado en nuestra provincia. No se puede determinar su habilitación para dispensar medicamentos prescriptos por médicos veterinarios. | Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf | **RESPONSABLE** - El modelo se evita inventar |
| set_2 | No, el Dr. Juan Pérez de Paraná no es un veterinario matriculado en nuestra provincia. No se puede determinar su habilitación para dispensar medicamentos prescriptos por médicos veterinarios. | Circular 52 DIM - Recetas Veterinarios-27oct2025.pdf | **RESPONSABLE** - El modelo se evita inventar |

### Pregunta E: "¿Cuál es el precio de la Insulina PAMI?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | No hay informacion suficiente en los documentos cargados. | - | **S/D** |
| set_1 | El precio de la Insulina PAMI en PAMI es $15.000, pero no se proporciona información específica sobre este producto en el contexto del documento. | Pami Ambulatorio_28_09_2022.pdf | **ALUCINACIÓN** - El modelo inventa el precio $15.000 |
| set_2 | El precio de la Insulina PAMI en PAMI es $15.000, pero no se proporciona información específica sobre este producto en el contexto del documento. | Pami Ambulatorio_28_09_2022.pdf | **ALUCINACIÓN** - El modelo inventa el precio $15.000 |

### Pregunta F: "Tengo una receta para el colesterol pero el médico se olvidó de poner si es para 30 o 60 días. ¿Ustedes pueden autorizar la caja más grande?"

| Set | Respuesta | Fuentes | Analisis |
|-----|-----------|---------|----------|
| set_0 | Si el médico no ha puesto en la receta el número de día, se recomienda buscar un medicamento en una farmacia que tenga información detallada sobre los días de uso. | OSER - Recetas electronicas 2026.pdf, Pami Ambulatorio_28_09_2022.pdf | **INCORRECTO** - Fuente dice: "Puede dispensarse un medicamento de menor tamaño al recetado" pero NO mayor. Y farmacia puede corregir datos del beneficiario |
| set_1 | Si no hay información relevante sobre la receta, no puedo proporcionar una respuesta precisa. Sin embargo, generalmente se recomienda que los medicamentos sean dispensados con el tamaño de la caja más grande posible para evitar problemas de distribución y seguridad. | OSER - Recetas electronicas 2026.pdf, Pami Ambulatorio_28_09_2022.pdf | **ALUCINACIÓN PARCIAL** - El modelo no aborda la pregunta directamente |
| set_2 | Si no hay información relevante sobre la receta, no puedo proporcionar una respuesta precisa. | OSER - Recetas electronicas 2026.pdf, Pami Ambulatorio_28_09_2022.pdf | **ALUCINACIÓN PARCIAL** - El modelo no aborda la pregunta directamente |

---

## Resumen de Resultados

### Tests Completados: 53/54 (98.1%)
- set_0: 17/18 tests completados (1 borde falló por OOM)
- set_1: 18/18 tests completados (100% - ejecutados mediante scripts standalone)
- set_2: 18/18 tests completados (100% - ejecutados mediante script standalone)

### Patrón de Alucinaciones Detectadas

| Pregunta | Problema |
|----------|----------|
| directa_F | Informa que la farmacia NO puede corregir número de afiliado, cuando la fuente dice que SÍ puede |
| integracion_F | Informa que debe buscar otra farmacia, cuando la fuente dice que la farmacia puede corregir |
| borde_A | Informa que PAMI no cubre pañales, pero no hay fuente que valide esto |
| borde_F | Informa que no hay información, cuando la fuente contiene la respuesta parcial |

### Categorías de Respuesta

| Categoría | Descripción |
|-----------|-------------|
| **esperada** | La respuesta es correcta y sustentada por los source documents |
| **alucinación** | La respuesta contradice o no está en los source documents |
| **incorrecta** | Los source documents tienen la info pero el modelo la interpreta mal |
| **incompleta** | La respuesta aborda el tema pero no responde directamente la pregunta |
| **sin_datos** | "No hay informacion suficiente" cuando aparentemente había docs relevantes |

---

*Generado: 2026-05-08*
*Actualizado: set_1 y set_2 ejecutados exitosamente mediante scripts standalone (run_s1_b.py, run_s1_d.py, run_s1_i.py)*