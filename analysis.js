function convertDataTime(data) {
    for(datum in data) {
        data[datum][0] = data[datum][0] * 1000;
    }
    return data;
}

// Takes {0 : v1, 1 : v2} to [[0, v1], [0, v2]]
function convertHashToArray(hash) {
    var retarray = [];
    for(key in hash) {
        retarray.push([key, hash[key]]);
    }
    return retarray;
}

// Takes {0 : [v11, v12], 1 : [v21, v22]} to [[0, v11, v12], [0, v21, v22]]
function convertHashArrayToArray(hash) {
    var retarray = [];
    for(key in hash) {
        var arrayentry = [key];
        for(entry in hash[key]) {
            arrayentry.push(hash[key][entry]);
        }
        retarray.push(arrayentry);
    }
    return retarray;
}

/* Turns
 * data['teams'][0] = { time -> {stat1 -> v1, stat2 -> v2}} into
 * [data['teams'][0]['stat1'][time] -> v1, data['teams'][0]['stat2'][time] -> v2]
 */
function convertTeamStatsToSingle(teamsData) {
    statList = [];
    splitStats = [{}, {}];
    for (time in teamsData[0]) {
        for (stat in teamsData[0][time]) {
            statList.push(stat);
            splitStats[0][stat] = {};
            splitStats[1][stat] = {};
        }
        break;
    }
    
    for(team in teamsData) {
        for(time in teamsData[team]) {
            for(stat in statList) {
                splitStats[team][statList[stat]][time] = teamsData[team][time][statList[stat]];
            }
        }
    }
    return splitStats;
}

//Get the time interval for which percent% of the time intervals are within
function getPercentTimeInterval(data, percent) {
    timeIntervals = [];
    lastTime = false;
    for(time in data) {
        if(lastTime == false) {
            lastTime = time;
            continue;
        }
        timeIntervals.push(time - lastTime);
        lastTime = time;
    }
    timeIntervals.sort();
    return timeIntervals[Math.floor((timeIntervals.length-1)*percent)];
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
    baseurl = "sample/";
    
    $.getJSON(baseurl+"data.json", function(data) {
        console.log(data);
        
        // Get last entry from objective data
        last_objective_entry = -1;
        for(i in data['objectives']['teams'][0]) {
            if(parseInt(i) > last_objective_entry) {
                last_objective_entry = parseInt(i);
            }
        }
        
        objectives_by_time = convertTeamStatsToSingle(data['objectives']['teams']);
        
        // Populate the scoreboard
        for(i = 0; i < 2; i++) {
            for(j = 0; j < 5; j++) {
                $("#detailed_scoreboard_champion_"+i+"_"+j).append("<td>"+championIconTag(data['game']['players'][i][j]['champion'])+"</td>");
                $("#detailed_scoreboard_champion_"+i+"_"+j).append(
                    "<td><span class='detailed_scoreboard_level'>"+data['game']['players'][i][j]['level']+"</span></td>");
                $("#detailed_scoreboard_champion_"+i+"_"+j).append(
                    "<td><span class='detailed_scoreboard_champion_name'>"+
                    printableChampionName(data['game']['players'][i][j]['champion'])+"</span><br />"+
                    "<span class='detailed_scoreboard_summoner_name'>"+quickfindLink(data['game']['players'][i][j]['summoner'])+"</span></td>");
                $("#detailed_scoreboard_champion_"+i+"_"+j).append("<td class='detailed_scoreboard_summoner_spells'></td>");
                for(k = 0; k < 2; k++) {
                    $("#detailed_scoreboard_champion_"+i+"_"+j+" .detailed_scoreboard_summoner_spells").append(summonerSpellIconTag(data['game']['players'][i][j]['summoner_spells'][k]));
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
            
            $("#main_scoreboard_"+i).append("<div class='main_scoreboard_kda'>"+data['game']['teams'][i]['kda'].join(" / ")+"</div>");
            $("#main_scoreboard_"+i).append("<div class='main_scoreboard_dragons'>Dragons: "+data['objectives']['teams'][i][last_objective_entry]['num_dragons']+"</div>");
            $("#main_scoreboard_"+i).append("<div class='main_scoreboard_barons'>Barons: "+data['objectives']['teams'][i][last_objective_entry]['num_barons']+"</div>");
            $("#main_scoreboard_"+i).append("<div class='main_scoreboard_cs'>CS: "+data['game']['teams'][i]['minions']+"</div>");
            $("#main_scoreboard_"+i).append("<div class='main_scoreboard_towers'>Towers: "+data['objectives']['teams'][i][last_objective_entry]['num_towers']+"</div>");
        }
        
        if(data['game']['teams'][0]['winner'] == true) {
            $("#winner").addClass("winner_blue_team");
            $("#winner").html("Blue Team Wins");
        }
        else {
            $("#winner").addClass("winner_purple_team");
            $("#winner").html("Purple Team Wins");
        }
        
        // Create the gold chart
        $('#team_gold_chart').highcharts('StockChart', {
            

            rangeSelector : {
                buttons: [{ type: 'minute', count: '3', text: '3m'}, { type: 'minute', count: '10', text: '10m'}, {type : 'all', text : "All"}],
                inputEnabled: false
            },

            title : {
                enabled: 'false'
            },
            
            xAxis: {
                type : 'datetime',
                ordinal : true
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
            
            plotOptions: {
                series : {
                    dataGrouping: {"units" : [['second', [1, 5]]], "approximation": "average"}
                }
            },
            
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
                    top: 295,
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
                    data : convertDataTime(convertHashToArray(data['gold']['teams'][0])),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#0046AF",
                    color: "#0046AF"
                },
                {
                    name : 'Purple Team',
                    data : convertDataTime(convertHashToArray(data['gold']['teams'][1])),
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
                    data : convertDataTime(convertHashToArray(data['gold']['difference'])),
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
        
        //Calculate accuracy of gold plots
        $("#gold_history_accuracy").text(getPercentTimeInterval(data['gold']['teams'][0], 0.99) / 2);
       
        plots = {"towers" : {title: "Towers"}, "dragons" : {title: "Dragons"}, "barons" : {title: "Barons"}};
        for(i in plots) {
            //Create the objective chart
            $('#team_'+i+'_chart').highcharts('StockChart', {
                rangeSelector : {
                    enabled: false
                },
    
                title : {
                    enabled: false
                },
                
                xAxis: {
                    type : 'datetime',
                    tickLength : 5,
                    minRange : 10000000
                },
                
                scrollbar : {
                    enabled: false
                },
                
                plotOptions: {
                    series : {
                        dataGrouping: {"units" : [['second', [5]]], "approximation": "open"}
                    }
                },
                
                tooltip: {
                    formatter: function() {
                        var s = '<b>'+ Highcharts.dateFormat('%H:%M:%S', this.x) +'</b>';
        
                        $.each(this.points, function(i, point) {
                            s += '<br/>'+ this.series.name + ": " + Math.round(point.y);
                        });
                    
                        return s;
                    },
                    useHTML: true
                },
                
                credits : false, 
                
                yAxis: [
                    {
                        title : { text: plots[i]['title'] },
                        min : 0,
                        lineWidth: 2,
                        minTickInterval: 1,
                        minorTickInterval: null
                    }
                    ],
                
                series : [
                    {
                        name : 'Blue Team '+plots[i]['title'],
                        data : convertDataTime(convertHashToArray(objectives_by_time[0]['num_'+i])),
                        tooltip: {
                            valueDecimals: 0
                        },
                        lineColor: "#0046AF",
                        color: "#0046AF",
                        step: true
                    },
                    {
                        name : 'Purple Team '+plots[i]['title'],
                        data : convertDataTime(convertHashToArray(objectives_by_time[1]['num_'+i])),
                        tooltip: {
                            valueDecimals: 0
                        },
                        lineColor: "#7000AD",
                        color: "#7000AD",
                        step: true
                    }
                ],
                
                navigator : {
                   enabled: false
                }
            });
        }
        
        //Calculate accuracy of objective plots
        $("#objective_history_accuracy").text(getPercentTimeInterval(objectives_by_time[0]['num_towers'], 0.99) / 2);
        
        //Inhibitors graph
        console.log(convertDataTime(convertHashArrayToArray(objectives_by_time[0]['num_inhibitors_range'])));
        $('#team_inhibitors_chart').highcharts('StockChart', {
            chart : {
                type: 'arearange'
            },
            
            rangeSelector : {
                enabled: false
            },

            title : {
                enabled: false
            },
            
            xAxis: {
                type : 'datetime',
                tickLength : 5,
                minRange : 10000000
            },
            
            scrollbar : {
                enabled: false
            },
            
            plotOptions: {
                series : {
                    dataGrouping: {"enabled" : false}
                }
            },
            
            tooltip: {
                formatter: function() {
                    var s = '<b>'+ Highcharts.dateFormat('%H:%M:%S', this.x) +'</b>';
    
                    $.each(this.points, function(i, point) {
                        s += '<br/>'+ this.series.name + ": " + Math.round(point.y);
                    });
                
                    return s;
                },
                useHTML: true
            },
            
            credits : false, 
            
            yAxis: [
                {
                    title : { text: "Blue Inhibs" },
                    min : 0,
                    max: 3,
                    offset: 0,
                    height: 100,
                    lineWidth: 2,
                    tickInterval: 1,
                    minorTickInterval: null
                },
                {
                    title : { text: "Purple Inhibs" },
                    min : 0,
                    max: 3,
                    offset: 0,
                    height: 100,
                    top: 120,
                    lineWidth: 2,
                    tickInterval: 1,
                    minorTickInterval: null
                }
                ],
            
            series : [
                {
                    name : 'Blue Team Inhibitors Taken',
                    data : convertDataTime(convertHashArrayToArray(objectives_by_time[0]['num_inhibitors_range'])),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#0046AF",
                    color: "#0046AF",
                    step: true
                },
                {
                    name : 'Purple Team Inhibitors Taken',
                    data : convertDataTime(convertHashArrayToArray(objectives_by_time[1]['num_inhibitors_range'])),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#7000AD",
                    color: "#7000AD",
                    step: true,
                    yAxis: 1
                }
            ],
            
            navigator : {
               enabled: false
            }
        });
    });
});
