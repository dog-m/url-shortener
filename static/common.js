function to_local_datetime(utc) {
    return new Date(utc + 'Z');
}

function to_local_datetime_ISO(utc) {
    // https://stackoverflow.com/a/51643788
    let t = to_local_datetime(utc);
    let z = t.getTimezoneOffset() * 60 * 1000;
    let tLocal = new Date(t - z);
    return tLocal.toISOString().split('.')[0];
}

function localize_time(utc) {
    let value = to_local_datetime(utc).toLocaleString();
    document.write(`<time>${value}</time>`);
}


// fix button-link behavior for styling
// inspired by https://stackoverflow.com/questions/33309632
document.addEventListener('DOMContentLoaded', () => {
    for (let link of document.querySelectorAll('a:has(button)')) {
        link.classList.add('no-drag');
        link.setAttribute('draggable', 'false');
        link.ondragstart = () => false;
        link.onmousedown = (e) => e.preventDefault();
        link.onmouseup   = (e) => e.preventDefault();
    }
});

