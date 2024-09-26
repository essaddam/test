// Créer un nouveau bouton avec les mêmes classes que les autres éléments de la page
const panelButton = document.createElement('button');
panelButton.innerText = 'Open Panel'; // Texte du bouton
panelButton.setAttribute('data-element-id', 'custom-panel-button'); // Ajouter un attribut personnalisé
panelButton.className = 'text-gray-400 hover:text-gray-500 dark:hover:text-white/80 h-1.5 transition-colors hidden'; // Classes de style similaires
panelButton.style.cssText = 'background: none; border: none; cursor: pointer; margin-left: 10px;';

// Trouver l'emplacement du bouton existant pour insérer le nouveau bouton à côté
const targetButton = document.querySelector('[data-element-id="width-control-button"]');
if (targetButton && targetButton.parentNode) {
  targetButton.parentNode.insertBefore(panelButton, targetButton.nextSibling);
}

// Créer le panneau similaire à une modale ou un panneau coulissant
const panel = document.createElement('div');
panel.id = 'custom-panel';
panel.className = 'fixed inset-0 bg-gray-800 bg-opacity-75 flex items-center justify-center z-[60] hidden'; // Style pour masquer et afficher en tant que modal
panel.style.cssText = `
  position: fixed;
  right: -300px;
  top: 20%;
  width: 300px;
  height: 400px;
  background-color: white;
  box-shadow: 0 4px 8px rgba(0,0,0,0.2);
  padding: 20px;
  transition: right 0.3s ease-in-out;
  z-index: 1000;
`;

// Contenu du panneau
panel.innerHTML = `
  <div class="text-gray-800 dark:text-white text-left text-sm">
    <h3 class="text-xl font-bold mb-4">Panneau</h3>
    <p>Ceci est un panneau que vous pouvez ouvrir et fermer.</p>
    <button id="close-panel" class="bg-red-500 text-white px-4 py-2 mt-4">Fermer</button>
  </div>
`;

// Ajouter le panneau au body de la page
document.body.appendChild(panel);

// Fonction pour afficher le panneau
function openPanel() {
  panel.style.right = '0'; // Faire glisser le panneau depuis la droite
  panel.classList.remove('hidden'); // Afficher le panneau
}

// Fonction pour masquer le panneau
function closePanel() {
  panel.style.right = '-300px'; // Masquer le panneau en le glissant à droite
  setTimeout(() => panel.classList.add('hidden'), 300); // Attendre la transition avant de masquer
}

// Ajouter un écouteur d'événement pour ouvrir le panneau au clic sur le bouton
panelButton.addEventListener('click', openPanel);

// Ajouter un écouteur d'événement pour fermer le panneau au clic sur le bouton de fermeture
document.getElementById('close-panel').addEventListener('click', closePanel);
