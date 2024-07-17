function toggleTable(name) {
    const board = document.getElementsByClassName(name)
    if (board?.length === 0) {
        return;
    }

    const button = board[0].querySelector("button.toggle");
    cur_table = document.querySelector(`board.${name} table.visible`);
    new_table = document.querySelector(`board.${name} table:not(.visible)`);
    if (!button || !cur_table || !new_table) {
        return;
    }

    new_table.classList.toggle("visible");
    cur_table.classList.toggle("visible");
    if (new_table.classList.contains("all")) {
        button.innerText = "All";
    }
    else {
        button.innerText = "Best";
    }
}