document.addEventListener("DOMContentLoaded", () => {
    manage_notifications_popup();
    manage_keyboard_input();
    manage_popups();
})

/**
 * Manages popups for each card element in the document.
 *
 * @return {void}
 */
function manage_popups(){
    document
        .querySelectorAll(".card")
        .forEach(create_popup_interactions)
}

/**
 * Creates popup interactions for a given card.
 *
 * @param {HTMLElement} card - The card element on which the popup interactions should be created.
 */
function create_popup_interactions(card){
    // Gérer les boutons pour ouvrir le popup de modification
    open_edit_popups_card(card);
    open_delete_popups_card(card);
}

/**
 * Opens the edit popups card.
 *
 * @param {HTMLElement} card - The HTML element representing the card.
 */
function open_edit_popups_card(card) {
    card.querySelectorAll(".popup_edit")
        .forEach(
            function(btn){
                btn.addEventListener(
                    "click",
                    () => open_edit_popup(card)
                )
            }
        )

    // Gérer le bouton pour fermer le popup
    let pb = card.querySelector(".popup.edit .popup_close")
    if (pb) {
        pb.addEventListener(
            "click",
            () => close_edit_popup(card)
        )
    }

        let pb_background = card.querySelector(".popup.edit")
    if (pb && pb_background) {
        pb_background.addEventListener(
            "click",
            (event) => {
                let classes = [...event.target.classList];
                if (classes.some((c) => c === "popup" || c === "edit")) {
                    close_edit_popup(card);
                }
            }
        )
    }
}


/**
 * Opens the edit popup for the given card element.
 *
 * @param {HTMLElement} card - The card element to open the edit popup for.
 *
 * @return {void}
 */
function open_edit_popup(card){
    let p = card.querySelector(".popup.edit");
    if (!p)
        return;

    p.classList.add("opened");
}

/**
 * Closes the edit popup for a given card.
 *
 * @param {HTMLElement} card - The card element containing the popup.
 */
function close_edit_popup(card){
    let p = card.querySelector(".popup.edit");
    if (!p)
        return;

    p.classList.remove("opened");
}


/**
 * Opens delete popups for a given card.
 *
 * @param {HTMLElement} card - The card element for which to open delete popups.
 */
function open_delete_popups_card(card) {
    // Icon "delete" in the card
    card.querySelectorAll(".popup_delete")
        .forEach(
            function(btn){
                btn.addEventListener(
                    "click",
                    () => open_delete_popup(card)
                )
            }
        )

    // Button "cancel" in the popup
    card.querySelectorAll(".popup.delete button.cancel")
        .forEach(
            function(btn){
                btn.addEventListener(
                    "click",
                    () => close_delete_popup(card)
                )
            }
        )

    // Gérer le bouton pour fermer le popup
    let pb = card.querySelector(".popup.delete .popup_close")
    if (pb) {
        pb.addEventListener(
            "click",
            () => close_delete_popup(card)
        )
    }

    let pb_background = card.querySelector(".popup.delete")
    if (pb && pb_background) {
        pb_background.addEventListener(
            "click",
            (event) => {
                let classes = [...event.target.classList];
                if (classes.some((c) => c === "popup" || c === "delete")) {
                    close_delete_popup(card);
                }
            }
        )
    }
}


/**
 * Opens the delete popup for a given card.
 *
 * @param {HTMLElement} card - The card element for which to open the delete popup.
 */
function open_delete_popup(card){
    let p = card.querySelector(".popup.delete");
    if (!p)
        return;

    p.classList.add("opened");
}

/**
 * Closes the delete popup if it exists.
 *
 * @param {HTMLElement} card - The card element containing the delete popup.
 */
function close_delete_popup(card){
    let p = card.querySelector(".popup.delete");
    if (!p)
        return;

    p.classList.remove("opened");
}

function manage_keyboard_input(){
    document.body.addEventListener(
        "keydown",
        (event) => {
            if (event.key.toLowerCase() === "escape") {
                document.querySelectorAll(".popup")
                    .forEach(
                        (p) => {
                            if (p.classList.contains("opened")) {
                                p.classList.remove("opened")
                            }
                        }
                    )
            }
        }
    )
}


function manage_notifications_popup(){
    let notifications = document.querySelectorAll(".notifications .notif");

    if (notifications.length < 1)
        return;

    notifications.forEach(function(elm){
        let x = elm.querySelector(".header svg");
        if (!x)
            console.warn("No close cross were found for the elm: ", elm)

        x.addEventListener(
            "click",
            () => elm.remove()
        )
    })
}