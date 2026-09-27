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


// https://stackoverflow.com/a/75988895
function debounce(callback, wait) {
    let timeoutId = null;
    return (...args) => {
        window.clearTimeout(timeoutId);
        timeoutId = window.setTimeout(() => {
            callback(...args);
        }, wait);
    };
}


function replaceHashtags(text, baseUrl) {
    return text.replace(
        /(?<!\w)#([\w-]+)/gu,
        (match, tag) => `<a href="${baseUrl}?q=${encodeURIComponent(match)}" class="hashtag">&num;${tag}&nbsp;🔎</a>`,
    );
}

function replaceHashtagsIn(element, baseUrl) {
    for (let description of element.getElementsByClassName('contains-hashtags')) {
        let source = description.innerHTML;
        if (source.includes('#'))
            description.innerHTML = replaceHashtags(source, baseUrl);
    }
}

