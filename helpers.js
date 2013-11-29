function championIconTag(name) {
    return "<img src='"+iconFolder+"champion-"+name+".png' class='icon champion_icon' />";
}

function itemIconTag(name) {
    return "<img src='"+iconFolder+"item-"+name+".png' class='icon item_icon' />";
}

function summonerSpellIconTag(name) {
    return "<img src='"+iconFolder+"summoner-"+name+".png' class='icon summoner_spell_icon' />";
}

function quickfindLink(summoner) {
    return "<a href='http://quickfind.kassad.in/profile/na/"+summoner+"'>"+summoner+"</a>";
}

function printableChampionName(name) {
    special_map = {};
    special_map['khazix'] = "Kha'Zix";
    special_map['kogmaw'] = "Kog'Maw";
    special_map['chogath'] = "Cho'gath";
    
    if(special_map[name]) {
        return special_map[name];
    }
    else {
        name = name.replace("-", " ");
        return name.replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
    }
} 