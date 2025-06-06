// на основе отметок типов шипов, алли, корп выставляет галочки на киллмылах
function UpdateKillmails()
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
    // вызваем пересчет средней цены
    updateAveragePrices();
    // вызываем копирование данных в поля ввода
    updateCompensationFields();
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


// рассчитывает средние цены среди выделенных киллмыл
function updateAveragePrices() {
    // Получаем все выделенные чекбоксы
    const checkedCheckboxes = document.querySelectorAll('.checkbox_killmails:checked');
    
    // Группируем строки по ship_id
    const ships = {};
    
    checkedCheckboxes.forEach(checkbox => {
        const row = checkbox.closest('tr');
        const shipId = checkbox.getAttribute('ship_id');
        const priceCell = row.querySelector('td:nth-child(9)'); // Ячейка с ценой (9-я td)
        const averagePriceCell = row.querySelector('td:nth-child(10)'); // Ячейка для средней цены (10-я td)
        
        // Извлекаем числовое значение цены (удаляем " kk ISK")
        const priceText = priceCell.textContent.trim();
        const price = parseFloat(priceText.replace(' kk ISK', ''));
        
        if (!ships[shipId]) {
            ships[shipId] = {
                prices: [],
                rows: []
            };
        }
        
        ships[shipId].prices.push(price);
        ships[shipId].rows.push(averagePriceCell);
    });
    
    // Для каждого типа корабля вычисляем среднее значение
    // алгритм такой - сначала вычисляем общее среднее, потом отбрасываем шипы
    // у которых цена выше средней и заново пересчитываем среднюю
    for (const shipId in ships) {
        const prices = ships[shipId].prices;
        // 1. Рассчитываем первоначальное среднее
        const full_average = prices.reduce((sum, price) => sum + price, 0) / prices.length;
        // 2. Фильтруем цены, оставляя только те, что <= full_average
        const filteredPrices = prices.filter(price => price <= full_average);
        // 3. Рассчитываем новое среднее только по отфильтрованным ценам
        const average = filteredPrices.reduce((sum, price) => sum + price, 0) / filteredPrices.length;
        // Обновляем все строки с этим ship_id
        ships[shipId].rows.forEach(cell => {
            cell.textContent = average.toFixed(2) + ' kk ISK';
        });
    };
}


// Функция для обновления полей компенсации в зависимости от выбранной радиокнопки
function updateCompensationFields() {
    const selectedRadio = document.querySelector('input[name="select_price"]:checked');
    if (!selectedRadio) return;
    
    const rows = document.querySelectorAll('tbody tr');
    rows.forEach(row => {
        const compensationInput = row.querySelector('td:nth-child(11) input[type="number"]');
        if (!compensationInput) return;
        
        // Определяем, из какого столбца брать значение
        let sourceCell;
        if (selectedRadio.value === 'select_price') {
            sourceCell = row.querySelector('td:nth-child(9)'); // Price
        } else {
            sourceCell = row.querySelector('td:nth-child(10)'); // Average price
        }
        
        if (sourceCell) {
            // Извлекаем числовое значение (удаляем " kk ISK")
            const valueText = sourceCell.textContent.trim();
            const value = parseFloat(valueText.replace(' kk ISK', ''));
            compensationInput.value = value.toFixed(0);
        }
    });
}


// выставляет управляющие чекбоксы и применяет их. Нужна как точка вызова нескольких функций
// вычисляет среднюю цену при старте
function ZeroState() {
    ZeroCheckes();
    UpdateKillmails();

    // Обработчики событий для чекбоксов
    const checkboxes = document.querySelectorAll('.checkbox_killmails');
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', () => {
            updateAveragePrices();
            updateCompensationFields();
        });
    });

    // Можно вызвать сразу при загрузке, чтобы обновить значения для уже выделенных строк
    updateAveragePrices();

    // Обработчики событий для радиокнопок
    const radioButtons = document.querySelectorAll('input[name="select_price"]');
    radioButtons.forEach(radio => {
        radio.addEventListener('change', updateCompensationFields);
    });

    // вызов при старте, чтобы копировалось значение независимо от того, какая цена выбрана
    updateCompensationFields();
}

document.addEventListener("DOMContentLoaded", ZeroState);
