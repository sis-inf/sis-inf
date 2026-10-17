from scripts.perfil.readme import reemplazar_bloque

INICIO="<!-- INICIO:proyectos -->"
FIN="<!-- FIN:proyectos -->"

def test_reemplaza():
    texto=INICIO+"\nviejo\n"+FIN
    resultado,cambio=reemplazar_bloque(texto,"proyectos","nuevo")

    assert cambio is True
    assert "viejo" not in resultado
    assert resultado==INICIO+"\nnuevo\n"+FIN

def test_marcadores():
    texto=INICIO+"\nviejo\n"+FIN
    resultado, cambio=reemplazar_bloque(texto,"proyectos","nuevo")

    assert INICIO in resultado
    assert FIN in resultado

def test_fuera():
    antes="# Título\n\nTexto previo.\n\n"
    despues="\n\nTexto posterior.\n"
    texto=antes+INICIO+"\nviejo\n"+FIN+despues
    resultado, cambio=reemplazar_bloque(texto,"proyectos","nuevo")

    assert resultado.startswith(antes)
    assert resultado.endswith(despues)

def test_idempotente():
    texto=INICIO+"\nviejo\n"+FIN
    una_vez, cambio1=reemplazar_bloque(texto,"proyectos","nuevo")
    dos_veces, cambio2=reemplazar_bloque(una_vez,"proyectos","nuevo")

    assert dos_veces==una_vez

def test_sin_marcadores():
    texto="# Título\n\nSin marcadores.\n"
    resultado,cambio=reemplazar_bloque(texto,"proyectos","nuevo")

    assert cambio is False
    assert resultado==texto

def test_sin_fin():
    texto=INICIO+"\nviejo\n"
    resultado,cambio=reemplazar_bloque(texto,"proyectos","nuevo")

    assert cambio is False
    assert resultado==texto

def test_sin_inicio():
    texto="\nviejo\n"+FIN
    resultado,cambio=reemplazar_bloque(texto,"proyectos","nuevo")

    assert cambio is False
    assert resultado==texto

def test_dos_bloques():
    inicio2="<!-- INICIO:lenguajes -->"
    fin2="<!-- FIN:lenguajes -->"
    bloque1=INICIO+"\nA\n"+FIN
    bloque2=inicio2+"\nB\n"+fin2
    texto=bloque1+"\n"+bloque2

    resultado,cambio=reemplazar_bloque(texto,"proyectos","nuevo")

    assert cambio is True
    assert INICIO+"\nnuevo\n"+FIN in resultado
    assert bloque2 in resultado
