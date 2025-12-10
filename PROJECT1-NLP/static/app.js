const btn = document.getElementById("btnPredict");
const textarea = document.getElementById("inputText");
const modelSelect = document.getElementById("modelSelect");
const resultContainer = document.getElementById("resultContainer");
const jsonResult = document.getElementById("jsonResult");
const entitySummary = document.getElementById("entitySummary");
const loading = document.getElementById("loading");
const errorBox = document.getElementById("errorBox");

btn.addEventListener("click", async () => {
  // Reset UI
  errorBox.classList.add("hidden");
  resultContainer.classList.add("hidden");
  
  const text = textarea.value.trim();
  const modelName = modelSelect.value;

  // Validation
  if (!text) {
    showError("Veuillez saisir un texte à analyser.");
    return;
  }
  if (!modelName) {
    showError("Veuillez sélectionner un modèle dans la liste.");
    return;
  }

  // Show loading
  loading.classList.remove("hidden");
  btn.disabled = true;

  try {
    const resp = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
          text: text,
          model_name: modelName
      })
    });

    const data = await resp.json();

    if (!resp.ok) {
        throw new Error(data.error || "Erreur serveur inconnue");
    }

    displayResults(data);

  } catch (err) {
    showError(err.message);
  } finally {
    loading.classList.add("hidden");
    btn.disabled = false;
  }
});

function showError(msg) {
    errorBox.textContent = msg;
    errorBox.classList.remove("hidden");
}

function displayResults(data) {
    resultContainer.classList.remove("hidden");
    
    // 1. Display JSON
    jsonResult.textContent = JSON.stringify(data.predictions, null, 2);

    // 2. Display Entity Chips
    entitySummary.innerHTML = "";
    if (data.entities && data.entities.length > 0) {
        data.entities.forEach(ent => {
            const chip = document.createElement("div");
            // Clean type name for CSS class (remove spaces, etc)
            const cssClass = ent.type.replace(/[^a-zA-Z0-9]/g, '_');
            chip.className = `chip ${cssClass}`;
            chip.innerHTML = `
                <span>${ent.text}</span>
                <span class="chip-type">${ent.type}</span>
            `;
            entitySummary.appendChild(chip);
        });
    } else {
        entitySummary.innerHTML = "<div class='chip Other'>Aucune entité détectée</div>";
    }
}
