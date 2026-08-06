let map;
let markers = [];

function DefaultMap() {
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 13,
        center: {
            lat: -26.1076,
            lng: 28.0567
        }
    });
}

const errorDiv = document.getElementById("error-message");

document.getElementById("search-btn").addEventListener("click", async () => {

    const address = document.getElementById("address-input").value;
    const type = document.getElementById("place-type").value;

    if (!address) {
        alert("Please enter an address!");
        return;
    }

    try {
        const response = await fetch(`/api/nearby?address=${encodeURIComponent(address)}&type=${type}`);

        const data = await response.json();

        if (!response.ok) {

            errorDiv.innerText = data.message || "Location not found.";

            errorDiv.style.display = "block";

            return;
        }

        if (data.results) {
            updateUI(data.results, data.location);
        }

    } catch (error) {

        console.error("API Error:", error);

        errorDiv.innerText = "Connection error. Is the Flask server running?";

        errorDiv.style.display = "block";
    }

});

function updateUI(places, location) {

    // Remove old markers
    markers.forEach(marker => marker.setMap(null));
    markers = [];

    // Clear previous results
    const list = document.getElementById("place-list");
    list.innerHTML = "";

    // Center the map
    map.setCenter(location);
    map.setZoom(14);

    places.forEach(place => {

        const marker = new google.maps.Marker({
            position: place.geometry.location,
            map: map,
            title: place.name
        });

        markers.push(marker);

        const li = document.createElement("li");
        
        li.className = "place-list";

        li.innerHTML = `
            <strong>${place.name}</strong><br>
            ${place.vicinity}<br>
            Rating: ${place.rating || "N/A"}
        `;

        list.appendChild(li);

    });

}

window.onload = DefaultMap;
