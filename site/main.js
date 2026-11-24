const button = document.querySelector("#copy-command");
const command = document.querySelector("#command-text");
const status = document.querySelector("#copy-status");

button?.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(command.textContent.trim());
    button.textContent = "Copiado";
    status.textContent = "Comandos copiados al portapapeles.";
  } catch {
    status.textContent = "Selecciona el bloque y cópialo manualmente.";
  }
  window.setTimeout(() => {
    button.textContent = "Copiar";
    status.textContent = "";
  }, 2200);
});
