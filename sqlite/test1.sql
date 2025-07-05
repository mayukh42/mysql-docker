select ar.Name as artist, 
    group_concat(distinct al.Title) as album, 
    group_concat(distinct tr.Name) as tracks
from tracks tr
    inner join albums al on tr.AlbumId = al.AlbumId
    inner join artists ar on al.ArtistId = ar.ArtistId
    group by artist;

