function inicio()
{
    var nuevaImagen = new Image();
    alert("Se procede a la carga en memoria de la imagen");
    nuevaImagen = cargarImagen("ejemplo.png");
}
function cargarImagen(url)
{
    var imagen = new Image();
    imagen.onload = imagenCargada;
    imagen.src = url;
    return imagen;
}
function imagenCargada()
{
    alert("La imagen se ha cargado correctamente");
}