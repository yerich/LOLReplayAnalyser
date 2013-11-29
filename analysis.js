iconFolder = "icons/";
lol_replay_data = 0;
lol_champion_data = 0;

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

// http://stackoverflow.com/questions/979975/how-to-get-the-value-from-url-parameter
// By SO user Quentin - CC-BY-SA 3.0
var QueryString = function () {
  // This function is anonymous, is executed immediately and 
  // the return value is assigned to QueryString!
  var query_string = {};
  var query = window.location.search.substring(1);
  var vars = query.split("&");
  for (var i=0;i<vars.length;i++) {
    var pair = vars[i].split("=");
        // If first entry with this name
    if (typeof query_string[pair[0]] === "undefined") {
      query_string[pair[0]] = pair[1];
        // If second entry with this name
    } else if (typeof query_string[pair[0]] === "string") {
      var arr = [ query_string[pair[0]], pair[1] ];
      query_string[pair[0]] = arr;
        // If third or later entry with this name
    } else {
      query_string[pair[0]].push(pair[1]);
    }
  } 
    return query_string;
} ();

/* Turns
 * data['teams'][0] = { time -> {stat1 -> v1, stat2 -> v2}} into
 * [data['teams'][0]['stat1'][time] -> v1, data['teams'][0]['stat2'][time] -> v2]
 */
function convertTeamStatsToSingle(teamsData) {
    statList = [];
    splitStats = [];
    for(team in teamsData) {
        splitStats.push({});
    }
    for (time in teamsData[0]) {
        for (stat in teamsData[0][time]) {
            statList.push(stat);
            for(team in teamsData) {
                splitStats[team][stat] = {};
            }
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

function convertPlayerStatsToSingle(playersData) {
    return [convertTeamStatsToSingle(playersData[0]), convertTeamStatsToSingle(playersData[1])];
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

$(document).ready(function() {
    if(QueryString.file)
        baseurl = QueryString.file+"/";
    else
        baseurl = "sample/";
    
    $.getJSON(baseurl+"data.json", function(data) {
        console.log(data);
        if(data['game']['clientVersion'] < "3.14")
            iconFolder = "icons/3.13/";
        
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
                    printableName(data['game']['players'][i][j]['champion'])+"</span><br />"+
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
                
                $("#champion_chart_selector").append("<option value='"+i+"_"+j+"' class='champion_chart_selector_team_"+i+"'>"+
                printableName(data['game']['players'][i][j]['champion'])+" ("+data['game']['players'][i][j]['summoner']+")</option>");
            }
            
            $("#main_scoreboard_"+i).append("<div class='main_scoreboard_gold'>"+Math.floor(data['game']['teams'][i]['gold'] / 100)/10+"k</div>");
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
        
        //Calculate the chart data for each chart
        var gold_by_time = convertTeamStatsToSingle(data['gold']['teams']);
        
        var chartData = {
            'goldHistory': {
                series : [
                    {
                        name : 'Blue Team Gold',
                        data : convertDataTime(convertHashToArray(gold_by_time[0]['total'])),
                        tooltip: {
                            valueDecimals: 0
                        },
                        lineColor: "#0046AF",
                        color: "#0046AF"
                    },
                    {
                        name : 'Purple Team Gold',
                        data : convertDataTime(convertHashToArray(gold_by_time[1]['total'])),
                        tooltip: {
                            valueDecimals: 0
                        },
                        lineColor: "#7000AD",
                        color: "#7000AD"
                    }
                ],
                yAxis : [
                    {
                        title : { text: "Gold Total" },
                        min : 0,
                        height: 220,
                        lineWidth: 2
                    }
                ]
            },
            'goldDifference': {
                series : [
                    {
                        name : 'Difference',
                        type : 'area',
                        data : convertDataTime(convertHashToArray(data['gold']['difference'])),
                        tooltip: {
                            valueDecimals: 0
                        },
                        color: "rgba(0, 0, 0, 0.3)",
                        fillColor: "rgba(0, 0, 0, 0.3)",
                        yAxisOffset: 0,
                    },
                    {
                        name : 'Difference2',
                        type : 'area',
                        fillColor : "#BFE3FF",
                        data : convertDataTime(convertHashToArray(data['gold']['difference'])),
                        tooltip: {
                            valueDecimals: 0
                        },
                        color: "#0046AF",
                        yAxisOffset: 0,
                        negativeColor: "#7000AD",
                        negativeFillColor: "#D6BFFF"
                    },
                ],
                yAxis: [
                    {
                        title : { text: "Gold Difference" },
                        height: 120,
                        top: 295,
                        offset: 0,
                        lineWidth: 2,
                        plotBands: [{
                          from: 0,
                          to: 10000000,
                          color: '#EFF8FF'
                        },
                        {
                          from: -10000000,
                          to: 0,
                          color: '#F5EFFF'
                        }]
                    }
                ]
            },
            'inhibitors' : {
                series: [
                    {
                        name : 'Blue Team Inhibitors Taken',
                        data : convertDataTime(convertHashArrayToArray(objectives_by_time[0]['num_inhibitors_range'])),
                        type : "arearange",
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
                        type : "arearange",
                        tooltip: {
                            valueDecimals: 0
                        },
                        lineColor: "#7000AD",
                        color: "#7000AD",
                        step: true,
                        yAxisOffset: 1
                    }
                ],
                yAxis: [
                    {
                        title : { text: "Blue Inhibs" },
                        min: 0,
                        max: 3,
                        offset: 0,
                        height: 80,
                        lineWidth: 2,
                        tickInterval: 1,
                        minorTickInterval: null,
                        fillColor: "#BFE3FF"
                    },
                    {
                        title : { text: "Purple Inhibs" },
                        min : 0,
                        max: 3,
                        offset: 0,
                        height: 80,
                        top: 120,
                        lineWidth: 2,
                        tickInterval: 1,
                        minorTickInterval: null,
                        fillColor: "#D6BFFF"
                    }
                ]
            }
        };
        
        var objectives_by_time = convertTeamStatsToSingle(data['objectives']['teams']);
        var team_kda_by_time = convertTeamStatsToSingle(data['kda']['teams']);
        var timePlots = {
            "cs" : {title: "Creep Score", height: 150, type: 'line', data : 
                [convertDataTime(convertHashToArray(objectives_by_time[0]['cs'])), 
                convertDataTime(convertHashToArray(objectives_by_time[1]['cs']))]},
            "towers" : {title: "Towers", height: 100, data : 
                [convertDataTime(convertHashToArray(objectives_by_time[0]['num_towers'])), 
                convertDataTime(convertHashToArray(objectives_by_time[1]['num_towers']))]}, 
            "dragons" : {title: "Dragons", height: 60, data : 
                [convertDataTime(convertHashToArray(objectives_by_time[0]['num_dragons'])), 
                convertDataTime(convertHashToArray(objectives_by_time[1]['num_dragons']))]}, 
            "barons" : {title: "Barons", height: 60, data : 
                [convertDataTime(convertHashToArray(objectives_by_time[0]['num_barons'])), 
                convertDataTime(convertHashToArray(objectives_by_time[1]['num_barons']))]},
            "kills" : {title: "Kills", height: 100, data : 
                [convertDataTime(convertHashToArray(team_kda_by_time[0]['kills'])), 
                convertDataTime(convertHashToArray(team_kda_by_time[1]['kills']))]},
            "deaths" : {title: "Deaths", height: 100, data : 
                [convertDataTime(convertHashToArray(team_kda_by_time[0]['deaths'])), 
                convertDataTime(convertHashToArray(team_kda_by_time[1]['deaths']))]},
            "assists" : {title: "Assists", height: 100, data : 
                [convertDataTime(convertHashToArray(team_kda_by_time[0]['assists'])), 
                convertDataTime(convertHashToArray(team_kda_by_time[1]['assists']))]},
            "currentlyDead" : {title: "# Currently Dead", height: 100, max : 5, data : 
                [convertDataTime(convertHashToArray(team_kda_by_time[0]['currently_dead'])), 
                convertDataTime(convertHashToArray(team_kda_by_time[1]['currently_dead']))]},
            "effectiveGold" : {title: "Effective Gold", height: 100, type : "line", data : 
                [convertDataTime(convertHashToArray(gold_by_time[0]['effective'])), 
                convertDataTime(convertHashToArray(gold_by_time[1]['effective']))]},
            "heldGold" : {title: "Held Gold", height: 100, type : "line", data : 
                [convertDataTime(convertHashToArray(gold_by_time[0]['held'])), 
                convertDataTime(convertHashToArray(gold_by_time[1]['held']))]}};
        
        for(i in timePlots) {
            chartData[i] = {
                series : [
                    {
                        name : 'Blue Team '+timePlots[i]['title'],
                        type : (timePlots[i]['type'] ? timePlots[i]['type'] : "area"),
                        data : timePlots[i]['data'][0],
                        tooltip: {
                            valueDecimals: 0
                        },
                        lineColor: "#0046AF",
                        color: "#0046AF",
                        fillColor : "rgba(147, 208, 255, 0.5)",
                        step: true
                    },
                    {
                        name : 'Purple Team '+timePlots[i]['title'],
                        type : (timePlots[i]['type'] ? timePlots[i]['type'] : "area"),
                        data : timePlots[i]['data'][1],
                        tooltip: {
                            valueDecimals: 0
                        },
                        lineColor: "#7000AD",
                        color: "#7000AD",
                        fillColor: "rgba(183, 147, 255, 0.5)",
                        step: true
                    }
                ],
                yAxis : [
                    {
                        title : { text: timePlots[i]['title'] },
                        min : 0,
                        max: (timePlots[i]['max'] ? timePlots[i]['max'] : undefined),
                        lineWidth: 2,
                        minTickInterval: 1,
                        minorTickInterval: null,
                        offset: 0,
                        height: timePlots[i]['height'],
                        minRange: 1
                    }
                ]
            };
        }
        
        lol_replay_data = chartData;
        drawMainChart(lol_replay_data);
        console.log(convertPlayerStatsToSingle(data['objectives']['players']));
        
        lol_champion_data = {
            "gold" : convertPlayerStatsToSingle(data['gold']['players']),
            "kda" : convertPlayerStatsToSingle(data['kda']['players']),
            "objectives" : convertPlayerStatsToSingle(data['objectives']['players']),
            "playerData" : data['game']['players'],
            "item_builds" : data['item_builds'],
            "skills" : data['skills']
        };
        printChampionDetails(lol_champion_data);
        
        //Calculate accuracy of gold plots
        $("#gold_history_accuracy").text(getPercentTimeInterval(data['gold']['teams'][0], 0.99) / 2);
        
        //Calculate accuracy of objective plots
        $("#objective_history_accuracy").text(getPercentTimeInterval(objectives_by_time[0]['num_towers'], 0.99) / 2);

        
        //Initalize Tabs
        $('.tab_container').tabs({ active: 0 });
        
        $("#main_chart_redraw").on("click", function(e) {
            drawMainChart(lol_replay_data);
        });
        
        $("#champion_chart_redraw").on("click", function(e) {
            printChampionDetails(lol_champion_data);
        });
        
        $("#loading").fadeOut();
    });
});
