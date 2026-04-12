// Inicializar galería al cargar la página
document.addEventListener("DOMContentLoaded", loadGallery);
document.getElementById("refreshBtn").addEventListener("click", loadGallery);

// Configuración de Auth traída del archivo config.js (inyectado por docker)
function getApiUrl() {
  const url = window.APP_CONFIG.API_URL.trim();
  return url.endsWith("/") ? url.slice(0, -1) : url;
}
function getToken() {
  return window.APP_CONFIG.API_TOKEN.trim();
}

function authHeaders() {
  return {
    Authorization: `Bearer ${getToken()}`,
  };
}

document
  .getElementById("imageForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const fileInput = document.getElementById("imageInput");
    const borderSize = document.getElementById("borderSize").value;
    const borderColor = document.getElementById("borderColor").value;

    const btn = document.getElementById("submitBtn");

    if (fileInput.files.length === 0) {
      showMessage("Por favor, selecciona una imagen", "error");
      return;
    }

    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("image", file);
    formData.append("size", borderSize);
    formData.append("color", borderColor);

    btn.disabled = true;
    btn.innerText = "Subiendo...";

    try {
      const apiUrl = getApiUrl();

      const response = await fetch(`${apiUrl}/upload`, {
        method: "POST",
        headers: authHeaders(), // Enviar Auth Token
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Error desconocido al subir la imagen");
      }

      showMessage(`¡Éxito! Imagen guardada como: ${data.filename}`, "success");
      fileInput.value = "";
      await loadGallery();
    } catch (error) {
      console.error("Error:", error);
      showMessage(error.message, "error");
    } finally {
      btn.disabled = false;
      btn.innerText = "Subir Imagen con Borde";
    }
  });

// Evento para borrar todas las imágenes
document
  .getElementById("deleteAllBtn")
  .addEventListener("click", async function () {
    if (
      !confirm(
        "¿Estás seguro que deseas eliminar TODAS las imágenes del servidor?",
      )
    )
      return;

    this.disabled = true;
    this.innerText = "Eliminando...";

    try {
      const apiUrl = getApiUrl();
      const response = await fetch(`${apiUrl}/images`, {
        method: "DELETE",
        headers: authHeaders(), // Enviar Auth Token
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Error al tratar de eliminar");
      }

      showMessage(data.message, "success");
      await loadGallery();
    } catch (error) {
      console.error("Error:", error);
      showMessage(error.message, "error");
    } finally {
      this.disabled = false;
      this.innerText = "Eliminar Todas";
    }
  });

function showMessage(message, type) {
  const msgBox = document.getElementById("messageBox");
  msgBox.innerText = message;
  msgBox.className = type;
}

async function loadGallery() {
  const apiUrl = getApiUrl();
  const token = getToken();
  const galleryDiv = document.getElementById("gallery");

  try {
    const response = await fetch(`${apiUrl}/images`, {
      method: "GET",
      headers: authHeaders(),
    });

    if (!response.ok) {
      console.error("No autorizado o error del Backend");
      return;
    }

    const images = await response.json();
    galleryDiv.innerHTML = "";

    if (images.length === 0) {
      galleryDiv.innerHTML = "<p>No hay imágenes subidas aún.</p>";
      return;
    }

    images.forEach((filename) => {
      const itemDiv = document.createElement("div");
      itemDiv.className = "gallery-item";

      const img = document.createElement("img");
      // Las imágenes no pueden mandar Authorization header fácilmente desde el src, pasamos token en el path.
      img.src = `${apiUrl}/uploads/${filename}?token=${token}`;
      img.alt = filename;

      const span = document.createElement("span");
      span.innerText = filename;

      itemDiv.appendChild(img);
      itemDiv.appendChild(span);
      galleryDiv.appendChild(itemDiv);
    });
  } catch (error) {
    console.error("Error cargando galería:", error);
  }
}
