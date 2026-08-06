let map;

function DefaultMap(){

    map = new google.maps.Map(
        document.getElementById("map"),
        {
            zoom:13,
            center:{
                lat:-26.1076,
                lng:28.0567
            }
        }
    );
}

document.getElementById("search-btn").addEventListener("click", async ()=>{

    const address = document.getElementById("address-input").value;

    const type = document.getElementById("place-type").value;

    const response = await fetch(`/api/nearby?address=${encodeURIComponent(address)}&type=${type}`);

    const data = await response.json();

    console.log(data);
});



window.onload = DefaultMap;
