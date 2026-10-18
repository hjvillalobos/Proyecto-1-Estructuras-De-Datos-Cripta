"""Trabajo de datos fuera de Tk; todos los eventos de ventana quedan en Tk."""
from threading import Thread
import tkinter as tk
import gc


def ejecutar_tarea(vista, funcion, *args, **kwargs):
    fin = tk.BooleanVar(master=vista.root, value=False)
    resultado, errores = [], []

    def trabajar():
        try:
            resultado.append(funcion(*args, **kwargs))
        except BaseException as error:
            errores.append(error)

    hilo = Thread(target=trabajar, name="cripta-datos")
    pendiente = None

    def comprobar():
        nonlocal pendiente
        if hilo.is_alive():
            pendiente = vista.root.after(15, comprobar)
        else:
            pendiente = None
            fin.set(True)

    vista._ocupada = True
    cursor = vista.root.cget("cursor")
    vista.root.configure(cursor="watch")
    def al_destruir(evento):
        nonlocal pendiente
        if evento.widget == vista.root:
            if pendiente is not None:
                vista.root.tk.call("after", "cancel", pendiente)
                pendiente = None
            fin.set(True)
    enlace = vista.root.bind("<Destroy>", al_destruir, add="+")
    # Los ciclos que contienen variables/imagenes Tk solo pueden destruirse en
    # el hilo de Tk. Una asignacion del motor no debe disparar su recoleccion.
    recolectaba = gc.isenabled()
    gc.disable()
    hilo.start()
    try:
        comprobar()
        if not fin.get():
            vista.root.wait_variable(fin)
    except tk.TclError:
        if not vista._cerrada:
            raise
    finally:
        # No se renueva/cierra la sesion mientras el trabajador la utiliza.
        hilo.join()
        if recolectaba:
            gc.enable()
        vista._ocupada = False
        if pendiente is not None:
            try:
                if vista._cerrada:
                    vista.root.tk.call("after", "cancel", pendiente)
                else:
                    vista.root.after_cancel(pendiente)
            except tk.TclError:
                pass
        if not vista._cerrada:
            vista.root.unbind("<Destroy>", enlace)
            vista.root.configure(cursor=cursor)
    if errores:
        raise errores[0]
    return resultado[0]
