function toggleSongList() {
    var songList = document.getElementById("song-list");
    var txtPlaylist = document.getElementById("lblCurplaylist");

    if (songList.style.display === "none") {
        songList.style.display = "block";
        txtPlaylist.textContent = "bravo"
    } else {
        songList.style.display = "none";
        txtPlaylist.textContent = "melong"
    }
}
