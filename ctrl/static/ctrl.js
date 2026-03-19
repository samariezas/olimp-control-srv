function timeAgo(isoStr) {
    var diff = Math.floor((Date.now() - new Date(isoStr).getTime()) / 1000);
    if (diff < 5) return 'ką tik';
    if (diff < 60) return 'prieš ' + diff + ' s';
    if (diff < 3600) return 'prieš ' + Math.floor(diff / 60) + ' min';
    if (diff < 86400) return 'prieš ' + Math.floor(diff / 3600) + ' val';
    return 'prieš ' + Math.floor(diff / 86400) + ' d';
}

function cleanUptime(str) {
    var m = str.match(/up\s+(\d+[:\s]\d+|\d+\s+days?)/i);
    return m ? m[1].trim() : str.trim();
}

function updateElapsed() {
    document.querySelectorAll('.last-seen[data-ts]').forEach(function(el) {
        el.textContent = timeAgo(el.getAttribute('data-ts'));
    });
    document.querySelectorAll('.uptime-value').forEach(function(el) {
        if (!el.dataset.cleaned) {
            el.textContent = cleanUptime(el.textContent);
            el.dataset.cleaned = '1';
        }
    });
}

function updateTimestamp() {
    var el = document.getElementById('last-updated');
    if (el) el.textContent = 'Atnaujinta: ' + new Date().toLocaleTimeString();
}

function startAutoRefresh(url, containerId, bannerId, onRefresh) {
    var container = document.getElementById(containerId);
    var banner = document.getElementById(bannerId);

    updateTimestamp();
    updateElapsed();

    setInterval(function() {
        fetch(url, {credentials: 'same-origin'})
            .then(function(r) {
                if (!r.ok) throw new Error(r.status);
                return r.text();
            })
            .then(function(html) {
                container.innerHTML = html;
                banner.style.display = 'none';
                if (onRefresh) onRefresh();
                updateTimestamp();
                updateElapsed();
            })
            .catch(function() {
                banner.style.display = 'block';
            });
    }, 5000);

    setInterval(updateElapsed, 1000);
}
