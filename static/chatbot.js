document.addEventListener("DOMContentLoaded", function () { 
    const messagesDiv = document.getElementById("messages");
    const inputField = document.getElementById("userInput");
    const sendButton = document.getElementById("sendMessageButton");
    let userName = null;
    let isMenuActive = false;

    function displayBotResponse(text) {
        console.log("Mostrando respuesta del chatbot:", text); // Verifica el contenido del mensaje
        const botMessage = document.createElement("p");
        botMessage.textContent = "IASmarBot: " + text;
        messagesDiv.appendChild(botMessage);
        messagesDiv.scrollTop = messagesDiv.scrollHeight; // Asegura que el scroll esté al final
    }

    function displayMainMenu() {
        console.log("Ejecutando displayMainMenu"); // Para confirmar que se ejecuta
        isMenuActive = true;
        displayBotResponse(
            "Por favor selecciona una opción:\n" +
            "1. Consultar productos disponibles.\n" +
            "2. Preguntas frecuentes sobre almacenamiento inteligente.\n" +
            "3. Hablar directamente con el IASmarBot."
        );
    }

    async function handleMenuSelection(option) {
        const normalizedOption = option.toLowerCase().trim();

        if (normalizedOption === "1" || normalizedOption.includes("consultar productos")) {
            await listAvailableProducts();
        } else if (normalizedOption === "2" || normalizedOption.includes("preguntas frecuentes")) {
            displayBotResponse(
                "Aquí tienes algunas preguntas frecuentes:\n" +
                "- ¿Qué tipos de productos ofrece IASmarEnergyStore?\n" +
                "- ¿Cómo optimizar el almacenamiento de energía?\n" +
                "- ¿Qué beneficios tiene el sistema inteligente de almacenamiento?"
            );
            displayMainMenu();
        } else if (normalizedOption === "3" || normalizedOption.includes("hablar directamente")) {
            isMenuActive = false; // Cambia a modo chat libre
            displayBotResponse("Perfecto, escribe tu pregunta y trataré de ayudarte.");
        } else {
            displayBotResponse("Opción no válida. Por favor selecciona 1, 2 o 3.");
            displayMainMenu();
        }
    }

    async function listAvailableProducts() {
        try {
            const response = await fetch("/list_products", {
                method: "GET",
                headers: { "Content-Type": "application/json" },
            });

            if (!response.ok) {
                displayBotResponse("No se pudieron obtener los productos. Intente más tarde.");
                return;
            }

            const data = await response.json();
            displayBotResponse("Productos disponibles:\n" + data.products.join("\n"));
            displayMainMenu();
        } catch (error) {
            displayBotResponse("Hubo un error de conexión. Intente nuevamente.");
        }
    }

    window.sendMessage = async function () {
        console.log("sendMessage se ejecutó correctamente.");
        const message = inputField.value.trim();
        if (!message) return;

        const userMessage = document.createElement("p");
        userMessage.textContent = "Tú: " + message;
        messagesDiv.appendChild(userMessage);

        try {
            if (!userName) {
                userName = message; // Guardar el nombre del usuario
                const response = await fetch("/set_name", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: userName }),
                });
                const data = await response.json();
                console.log("Respuesta del servidor:", data); // Mostrar la respuesta del servidor
                displayBotResponse(data.message);
                displayMainMenu(); // Llamar al menú principal después de recibir el nombre
                console.log("displayMainMenu ejecutado."); // Confirmar que la función se ejecuta
                inputField.value = "";
                return;
            }

            if (isMenuActive) {
                await handleMenuSelection(message);
            } else {
                const response = await fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ question: message }),
                });
                const data = await response.json();
                displayBotResponse(data.response || "Lo siento, no entiendo la pregunta.");
            }
        } catch (error) {
            displayBotResponse("Hubo un error de conexión.");
        }

        inputField.value = "";
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };

    sendButton.addEventListener("click", sendMessage);

    inputField.addEventListener("keypress", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    displayBotResponse("¡Hola! Soy IASmarBot, tu asistente de almacenamiento inteligente. ¿Cómo te llamas?");
    displayMainMenu();
});
