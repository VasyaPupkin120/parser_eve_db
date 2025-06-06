// на основе отметок типов шипов, алли, корп выставляет галочки на киллмылах
function UpdateKillmails(button)
{
    checkboxes_shiptypes = document.getElementsByClassName('checkbox_shiptypes');
    checkboxes_alliances = document.getElementsByClassName('checkbox_alliances');
    checkboxes_corporations = document.getElementsByClassName('checkbox_corporations');
    checkboxes_killmails = document.getElementsByClassName('checkbox_killmails');


    var checked_ships = [];
    var checked_alliances = [];
    var checked_corporations = [];

    // отмеченные шипы
    for (var i=0; i<checkboxes_shiptypes.length; i++) {
        if (checkboxes_shiptypes[i].checked) {
            checked_ships.push(checkboxes_shiptypes[i].getAttribute("ship_id"))
        }
    }
    // отмеченные алли
    for (var i=0; i<checkboxes_alliances.length; i++) {
        if (checkboxes_alliances[i].checked) {
            checked_alliances.push(checkboxes_alliances[i].getAttribute("alliance_id"))
        }
    }
    // отмеченные корпы
    for (var i=0; i<checkboxes_corporations.length; i++) {
        if (checkboxes_corporations[i].checked) {
            checked_corporations.push(checkboxes_corporations[i].getAttribute("corporation_id"))
        }
    }

    // выставляем галочки на киллмылах
    for (var i=0; i<checkboxes_killmails.length; i++) {
        killmail_ship_id = checkboxes_killmails[i].getAttribute("ship_id");
        killmail_alliance_id = checkboxes_killmails[i].getAttribute("alliance_id");
        killmail_corporation_id = checkboxes_killmails[i].getAttribute("corporation_id");
        this_ship_checked = checked_ships.includes(killmail_ship_id);
        this_alliance_checked = checked_alliances.includes(killmail_alliance_id);
        this_corporation_checked = checked_corporations.includes(killmail_corporation_id);

        if (this_ship_checked && (this_alliance_checked || this_corporation_checked)) {
            checkboxes_killmails[i].checked = true
        }
        else {
            checkboxes_killmails[i].checked = false
        }
    }
}

function SetCheckboxesInThisBlock(button)
{
    var block = button.parentElement;
    var checkboxes = block.getElementsByTagName('input');
    for (var i=0; i<checkboxes.length; i++) {
        checkboxes[i].checked = true;
    }
}

function ClearCheckboxesInThisBlock(button)
{
    var block = button.parentElement;
    var checkboxes = block.getElementsByTagName('input');
    for (var i=0; i<checkboxes.length; i++) {
        checkboxes[i].checked = false;
    }
}

// состояния управляющих чекбоксов в самом начале.
function ZeroCheckes() {
    checkboxes_shiptypes = document.getElementsByClassName('checkbox_shiptypes');
    checkboxes_alliances = document.getElementsByClassName('checkbox_alliances');
    checkboxes_corporations = document.getElementsByClassName('checkbox_corporations');
    checkboxes_killmails = document.getElementsByClassName('checkbox_killmails');

    unchecked_ships_id = [
        "670",  //Capsule
        "33328" //genolution auroral capsule
    ]
    checked_alliances_id = [
        "99012122",  //HOLD MY PROBS
        "99012328",  //STAKAN UNIVERSE
        "99011248",  //Big Green Fly 
        "99012287"   //New Horizons all
    ];
    checked_corporations_id = [
        "98733526" //Prom Teh Akadem
    ];

    for (var i=0; i<checkboxes_shiptypes.length; i++) {
        ship_id = checkboxes_shiptypes[i].getAttribute("ship_id");
        this_ship_checked = !unchecked_ships_id.includes(ship_id);
        if (this_ship_checked) {
            checkboxes_shiptypes[i].checked = true;
        }
        else {
            checkboxes_shiptypes[i].checked = false;
        }
    }
    for (var i=0; i<checkboxes_alliances.length; i++) {
        alliance_id = checkboxes_alliances[i].getAttribute("alliance_id");
        this_alliance_checked = checked_alliances_id.includes(alliance_id);
        if (this_alliance_checked) {
            checkboxes_alliances[i].checked = true;
        }
        else {
            checkboxes_alliances[i].checked = false;
        }
    }
    for (var i=0; i<checkboxes_corporations.length; i++) {
        corporation_id = checkboxes_corporations[i].getAttribute("corporation_id");
        this_corporation_checked = checked_corporations_id.includes(corporation_id);
        if (this_corporation_checked) {
            checkboxes_corporations[i].checked = true;
        }
        else {
            checkboxes_corporations[i].checked = false;
        }
    }


}
// выставляет управляющие чекбоксы и применяет их. Нужна как точка вызова нескольких функций
function ZeroState() {
    ZeroCheckes();
    UpdateKillmails();

}

document.addEventListener("DOMContentLoaded", ZeroState);
