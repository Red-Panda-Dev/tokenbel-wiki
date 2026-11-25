import { mount } from "pele";

for (const container of document.querySelectorAll("[data-mermaid]")) {
  const source = container.textContent.trim();
  mount(container, source, {
    zoom: false,
    onError(error) {
      // Keep the labels and connections readable even for an unsupported block.
      container.textContent = source;
      console.warn("Не удалось отобразить схему:", error);
    },
  });
}
