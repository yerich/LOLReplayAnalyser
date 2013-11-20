function convertDataTime(data) {
    for(datum in data) {
        data[datum][0] = data[datum][0] * 1000;
    }
    return data;
}

function championIconTag(name) {
    return "<img src='icons/champion-"+name+".png' />";
}

function itemIconTag(name) {
    return "<img src='icons/item-"+name+".png' />";
}

function summonerSpellIconTag(name) {
    return "<img src='icons/summoner-"+name+".png' />";
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

$(document).ready(function() {
    baseurl = "output/sample/";
    
    $.getJSON(baseurl+"data.json", function(data) {
        console.log(data);
        
        // Populate the scoreboard
        for(i = 0; i < 2; i++) {
            for(j = 0; j < 5; j++) {
                $("#main_scoreboard_champion_"+i+"_"+j).html(championIconTag(data['game']['players'][i][j]['champion']));
                $("#detailed_scoreboard_champion_"+i+"_"+j).append("<td>"+championIconTag(data['game']['players'][i][j]['champion'])+"</td>");
                $("#detailed_scoreboard_champion_"+i+"_"+j).append(
                    "<td><span class='detailed_scoreboard_level'>"+data['game']['players'][i][j]['level']+"</span></td>");
                $("#detailed_scoreboard_champion_"+i+"_"+j).append(
                    "<td><span class='detailed_scoreboard_champion_name'>"+
                    printableChampionName(data['game']['players'][i][j]['champion'])+"</span><br />"+
                    "<span class='detailed_scoreboard_summoner_name'>"+quickfindLink(data['game']['players'][i][j]['summoner'])+"</span></td>");
                $("#detailed_scoreboard_champion_"+i+"_"+j).append("<td class='detailed_scoreboard_summoner_spells'></td>");
                for(k = 0; k < 2; k++) {
                    $("#detailed_scoreboard_champion_"+i+"_"+j+" .detailed_scoreboard_summoner_spells").append(summonerSpellIconTag(data['game']['players'][i][j]['summoner-spells'][k]));
                }
                $("#detailed_scoreboard_champion_"+i+"_"+j).append("<td class='detailed_scoreboard_items'></td>");
                for(k = 0; k < data['game']['players'][i][j]['items'].length; k++) {
                    $("#detailed_scoreboard_champion_"+i+"_"+j+" .detailed_scoreboard_items").append(itemIconTag(data['game']['players'][i][j]['items'][k]));
                }
                $("#detailed_scoreboard_champion_"+i+"_"+j).append(
                    "<td><span class='detailed_scoreboard_level'>"+data['game']['players'][i][j]['kda'].join(" / ")+"</span></td>");
                $("#detailed_scoreboard_champion_"+i+"_"+j).append(
                    "<td><span class='detailed_scoreboard_level'>"+data['game']['players'][i][j]['minions']+"</span></td>");
                $("#detailed_scoreboard_champion_"+i+"_"+j).append(
                    "<td><span class='detailed_scoreboard_level'>"+data['game']['players'][i][j]['total_gold']+"</span></td>");
            }
        }
        
        // Create the gold chart
        $('#team_gold_chart').highcharts('StockChart', {
            

            rangeSelector : {
                buttons: [{ type: 'minute', count: '3', text: '3m'}, { type: 'minute', count: '10', text: '10m'}, {type : 'all', text : "All"}],
                inputEnabled: false
            },

            title : {
                text : 'Gold over time'
            },
            
            xAxis: {
                type : 'datetime'
            },
            
            tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%H:%M:%S', this.x) +'</b>';
    
                    $.each(this.points, function(i, point) {
                        if(this.series.name == "Difference") {
                            if(point.y == 0)
                                s += '<br/>Tied';
                            else if(point.y > 0)
                                s += '<br/><span style="color: #0046AF;"><strong>Blue team leads</strong></span> by ' + Math.round(point.y);
                            else
                                s += '<br/><span style="color: #7000AD;"><strong>Purple team leads</strong></span> by ' + Math.round(-point.y);
                        }
                        else {
                            s += '<br/>'+ this.series.name + ": " + Math.round(point.y);
                        }
                    });
                
                    return s;
                },
                useHTML: true
            },
            
            credits : false, 
            
            yAxis: [
                {
                    title : { text: "Total" },
                    min : 0,
                    height: 250,
                    lineWidth: 2
                },
                {
                    title : { text: "Difference" },
                    height: 150,
                    top: 325,
                    offset: 0,
                    lineWidth: 2,
                    plotBands: [{
                      from: 0,
                      to: 10000000,
                      color: '#DDF0FF'
                    },
                    {
                      from: -10000000,
                      to: 0,
                      color: '#E0DDFF'
                    }]
                }
                ],
            
            series : [
                {
                    name : 'Blue Team',
                    data : convertDataTime(data['gold']['teams'][0]),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#0046AF",
                    color: "#0046AF"
                },
                {
                    name : 'Purple Team',
                    data : convertDataTime(data['gold']['teams'][1]),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#7000AD",
                    color: "#7000AD"
                },
                {
                    name : 'Difference',
                    type : 'area',
                    fillColor : "rgba(0, 0, 0, 0.3)",
                    data : convertDataTime(data['gold']['difference']),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#000",
                    color: "#000",
                    yAxis: 1
                }
            ],
            
            navigator : {
                baseSeries: 2
            }
        });
    });
});
