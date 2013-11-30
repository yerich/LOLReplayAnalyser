function secondsToMinSeconds(seconds) {
    var dispseconds = seconds % 60;
    if(dispseconds < 10) {
        dispseconds = "0"+dispseconds;
    }
    var dispminutes = Math.floor(seconds / 60);
    return dispminutes+":"+dispseconds;
}

function drawMainChart(chartData) {
    // Create the main chart
    main_chart = { series: [], yAxis: []};
    plots = [];
    
    $("#main_chart_selector input").each(function(k, v) {
        if($(v).is(':checked'))
            plots.push($(v).val());
    });
    var yAxiscount = 0;
    chartHeight = 120;
    for(plot in plots) {
        p = plots[plot];
        for(j in chartData[p]['series']) {
            if(chartData[p]['series'][j].yAxisOffset)
                chartData[p]['series'][j].yAxis = parseInt(chartData[p]['series'][j].yAxisOffset) + parseInt(yAxiscount);
            else
                chartData[p]['series'][j].yAxis = parseInt(yAxiscount);
            main_chart['series'].push(chartData[p]['series'][j]);
        }
        
        for(j in chartData[p]['yAxis']) {
            chartData[p]['yAxis'][j].top = chartHeight - 85;
            chartData[p]['yAxis'][j].plotLines = [{ color: '#333', value: 0, width: 1, zIndex: 5}];
            main_chart['yAxis'].push(chartData[p]['yAxis'][j]);
            chartHeight += chartData[p]['yAxis'][j]['height'] + 10;
            yAxiscount += 1;
        }
    }
    console.log(yAxiscount);
    
    $("#main_chart").height(chartHeight);
    
    $('#main_chart').highcharts('StockChart', {
        rangeSelector : {
            buttons: [{ type: 'minute', count: '3', text: '3m'}, { type: 'minute', count: '10', text: '10m'}, {type : 'all', text : "All"}],
            inputEnabled: false
        },

        title : {
            enabled: 'false'
        },
        
        xAxis: {
            type : 'datetime',
            ordinal : false,
            gridLineWidth: 0,
            labels: { formatter: function () {
                return secondsToMinSeconds(this.value/1000);
            }}
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
                    else if(this.series.name.substring(0, "Blue Team".length) == "Blue Team") {
                        s += "<br/>" + this.series.name.substring("Blue Team".length) + ': <span style="color: #0046AF;"><strong>'+Math.round(point.y)+"</strong></span>";
                    }
                    else if(this.series.name.substring(0, "Purple Team".length) == "Purple Team") {
                        s += ' | <span style="color: #7000AD;"><strong>'+Math.round(point.y)+"</strong></span>";
                    }
                    else if(this.series.name == "Difference2") {
                        return;
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
            line : {
                dataGrouping: {"units" : [['second', [1, 5]]], "approximation": "open"}
            },
            area : {
                dataGrouping: {"units" : [['second', [1, 5]]], "approximation": "open"}
            },
        },
        
        yAxis: main_chart['yAxis'],
        series : main_chart['series'],
        
        navigator : {
            baseSeries: 2,
            color: "#000",
            fillColor: "#FFF",
            negativeColor: "#000",
            negativeFillColor: "#FFF",
            xAxis: { labels: { formatter: function () {
                var seconds = (this.value / 1000);
                var dispseconds = seconds % 60;
                if(dispseconds < 10) {
                    dispseconds = "0"+dispseconds;
                }
                var dispminutes = Math.floor(seconds / 60);
                return dispminutes+":"+dispseconds;
            }}}
        }
    });
}

function printChampionDetails(data) {
    var selectedChampion = $("#champion_chart_selector").val().split("_");
    var selectedChampionName = data['playerData'][selectedChampion[0]][selectedChampion[1]]['champion'];
    var selectedChampionLineColor = "#DD2A00";
    var selectedChampionFillColor = "rgba(221, 42, 0, 0.4)";
    
    var compareChampions = [];
    
    for(var i = 0; i < 5; i++) {
        var compareChampion = $("#champion_chart_compare_"+i).val();
        if(!compareChampion)
            break;
        compareChampions.push(compareChampion.split("_"));
    }
    
    var compareChampionsNames = [];
    var compareChampionsLineColors = ["#E2A600", "#3ADB00", "#00D8D8", "#0011D6"];
    var compareChampionsFillColors = ["rgba(143, 105, 0, 0.4)", "rgba(58, 219, 0, 0.4)", "rgba(0, 216, 216, 0.4)", "rgba(0, 17, 214, 0.4)"];
    for(var champion in compareChampions) {
        compareChampionsNames[champion] = data['playerData'][compareChampions[champion][0]][compareChampions[champion][1]]['champion'];
    }
    
    //Output champion skill order
    $("#champion_skill_order_table").html("");
    $("#champion_skill_order_table").append("<tr><th></th></tr>");
    for(var i = 1; i <= 18; i++) {
        $("#champion_skill_order_table tr:last-child").append("<th>"+i+"</th>");
    }
    var skill_names = ["Q", "W", "E", "R"];
    for(var i = 0; i < 4; i++) {
        //First (legend) cell in the table
        $("#champion_skill_order_table").append("<tr><td>"+skill_names[i]+"</td></tr>");
        for(var j = 0; j < 18; j++) {   //18 cells, one for each skill point
            //Occasionally, someone may assign skill points rapidly, so we don't catch which one came first
            //In this case we have to combine the cells into one
            if(data['skills']['order'][selectedChampion[0]][selectedChampion[1]].length > j) {
                var leveledSkills = data['skills']['order'][selectedChampion[0]][selectedChampion[1]][j];
                var skillLeveled = false;
                for(skill in leveledSkills) {
                    if(leveledSkills[skill] == i) {
                        if(skillLeveled == true)
                            $("#champion_skill_order_table tr:last-child td:last-child").append("&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&bull;");
                        else
                            $("#champion_skill_order_table tr:last-child").append("<td class='champion_skill_order_table_selected' colspan='"+leveledSkills.length+"'>&bull;</td>");
                        skillLeveled = true;
                    }
                }
                if(skillLeveled == false) {
                    $("#champion_skill_order_table tr:last-child").append("<td colspan='"+leveledSkills.length+"'></td>");
                }
                j += leveledSkills.length - 1;
            }
            else
                $("#champion_skill_order_table tr:last-child").append("<td></td>");
        }
    }
    
    //Output champion build order
    $("#champion_build_order").html("");
    var counter = 0;
    for(index in data['item_builds']['builds'][selectedChampion[0]][selectedChampion[1]]) {
        var entry = data['item_builds']['builds'][selectedChampion[0]][selectedChampion[1]][index];
        if(selectedChampion[0] == 0)
            entry[1] = entry[1].reverse();
        if(counter == 0) {
            $("#champion_build_order").append("<div><span class='champion_build_order_time'>Start</span><span class='champion_build_order_items'></span></div>");
        }
        else {
            $("#champion_build_order").append("<div><span class='champion_build_order_time'>"+secondsToMinSeconds(entry[0])+
                "</span><span class='champion_build_order_raquo'>&raquo;</span><span class='champion_build_order_items'></span></div>");
        }
        
        for(k = 0; k < entry[1].length; k++) {
            $("#champion_build_order div:last-child .champion_build_order_items").append(itemIconTag(entry[1][k]));
        }
        if(entry[2].length > 0 && entry[1].length == 0) {
            for(k = 0; k < entry[2].length; k++) {
                $("#champion_build_order div:last-child .champion_build_order_items").append("<span class='champion_build_order_item_sold'><span></span>"+
                    itemIconTag(entry[2][k]))+"</span>";
            }
        }
        counter ++;
    }
    
    //Output champion build history
    $("#champion_item_history tbody").html("");
    for(time in data['item_builds']['history'][selectedChampion[0]][selectedChampion[1]]) {
        if(selectedChampion[0] == 1)
            var entry = data['item_builds']['history'][selectedChampion[0]][selectedChampion[1]][time];
        else
            var entry = data['item_builds']['history'][selectedChampion[0]][selectedChampion[1]][time].reverse();
        $("#champion_item_history tbody").append("<tr><td>"+secondsToMinSeconds(time)+"</td><td class='champion_item_history_items'></td></tr>");
        for(k = 0; k < entry.length; k++) {
            $("#champion_item_history tbody tr:last-child .champion_item_history_items").append(itemIconTag(entry[k]));
        }
    }
    
    //Draw history chart
    chartData = {
        "championGoldHistory" : {
            series : [
                {
                    name : "gold",
                    dataFunction : function(champData, team, player) {
                        return convertDataTime(convertHashToArray(champData['gold'][team][player]['total']));
                    },
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: selectedChampionLineColor,
                    color: selectedChampionLineColor
                }
            ],
            yAxis : [
                {
                    title : { text: "Gold Total" },
                    min : 0,
                    height: 220,
                    offset: 0,
                    lineWidth: 2
                }
            ]
        },
        "gpm" : {
            series : [
                {
                    name : "gpm (last 1 min.)",
                    dataFunction : function(champData, team, player) {
                        return convertDataTime(convertHashToArray(champData['gold'][team][player]['gpm1']));
                    },
                    tooltip: {
                        valueDecimals: 2
                    },
                    lineColor: "#FFC0B5",
                    color: "#FFC0B5",
                    skipComparison: true
                },
                {
                    name : "gpm (last 5 min.)",
                    dataFunction : function(champData, team, player) {
                        return convertDataTime(convertHashToArray(champData['gold'][team][player]['gpm5']));
                    },
                    tooltip: {
                        valueDecimals: 2
                    },
                    lineColor: "#E07D67",
                    color: "#E07D67",
                    skipComparison: true
                },
                {
                    name : "gpm (cumulative)",
                    dataFunction : function(champData, team, player) {
                        return convertDataTime(convertHashToArray(champData['gold'][team][player]['gpm']));
                    },
                    tooltip: {
                        valueDecimals: 2
                    },
                    lineColor: selectedChampionLineColor,
                    color: selectedChampionLineColor
                },
            ],
            yAxis : [
                {
                    title : { text: "Gold/Min." },
                    min : 0,
                    height: 120,
                    offset: 0,
                    lineWidth: 2
                }
            ]
        },
        "championCSHistory" : {
            series : [
                {
                    name : "creep score",
                    dataFunction : function(champData, team, player) {
                        return convertDataTime(convertHashToArray(champData['objectives'][team][player]['minions']));
                    },
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: selectedChampionLineColor,
                    color: selectedChampionLineColor
                }
            ],
            yAxis : [
                {
                    title : { text: "Creep Score" },
                    min : 0,
                    height: 120,
                    offset: 0,
                    lineWidth: 2
                }
            ]
        },
        "championIsDead" : {
            series : [
                {
                    name : "is dead",
                    type : 'area',
                    step : 'true',
                    dataFunction : function(champData, team, player) {
                        return convertDataTime(convertHashToArray(champData['kda'][team][player]['is_dead']));
                    },
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: selectedChampionLineColor,
                    lineWidth: 0,
                    fillColor: selectedChampionFillColor,
                    color: selectedChampionLineColor
                }
            ],
            yAxis : [
                {
                    title : { text: "Dead?" },
                    min : 0,
                    max : 1,
                    gridLineWidth: 0,
                    minorGridLineWidth: 0,
                    height: 20,
                    offset: 0,
                    lineWidth: 2
                }
            ]
        }
    };
    
    champion_chart = {series : [], yAxis : []};
    plots = ["championGoldHistory", "gpm", "championCSHistory", "championIsDead"];
    var yAxiscount = 0;
    chartHeight = 120;
    for(plot in plots) {
        p = plots[plot];
        for(j in chartData[p]['series']) {
            if(compareChampions.length > 0 && chartData[p]['series'][j].skipComparison)
                continue;
            
            if(chartData[p]['series'][j].yAxisOffset)
                chartData[p]['series'][j].yAxis = parseInt(chartData[p]['series'][j].yAxisOffset) + parseInt(yAxiscount);
            else
                chartData[p]['series'][j].yAxis = parseInt(yAxiscount);
            chartData[p]['series'][j].data = chartData[p]['series'][j].dataFunction(data, selectedChampion[0], selectedChampion[1]);
            chartData[p]['series'][j].origName = chartData[p]['series'][j].name;
            chartData[p]['series'][j].name = printableName(selectedChampionName) + " " + chartData[p]['series'][j].origName;
            chartData[p]['series'][j].primarySeries = true;
            chartData[p]['series'][j].championName = printableName(selectedChampionName);
            var newseries = $.extend(new chartData[p]['series'][j].constructor, chartData[p]['series'][j]);
            champion_chart['series'].push(newseries);
        }
        
        for(j in chartData[p]['yAxis']) {
            chartData[p]['yAxis'][j].top = chartHeight - 85;
            chartData[p]['yAxis'][j].plotLines = [{ color: '#333', value: 0, width: 1, zIndex: 5}];
            champion_chart['yAxis'].push(chartData[p]['yAxis'][j]);
            chartHeight += chartData[p]['yAxis'][j]['height'] + 10;
            yAxiscount += 1;
        }
    }
    
    compareChampionsMode = false;
    for(champion in compareChampions) {
        champion = parseInt(champion);
        var yAxiscount = 0;
        var seriesCount = 0;
        compareChampionsMode = true;
        for(plot in plots) {
            p = plots[plot];
            for(j in chartData[p]['series']) {
                if(chartData[p]['series'][j].skipComparison)
                    continue;
                
                if(chartData[p]['series'][j].yAxisOffset)
                    chartData[p]['series'][j].yAxis = parseInt(chartData[p]['series'][j].yAxisOffset) + parseInt(yAxiscount);
                else
                    chartData[p]['series'][j].yAxis = parseInt(yAxiscount);
                chartData[p]['series'][j].data = chartData[p]['series'][j].dataFunction(data, compareChampions[champion][0], compareChampions[champion][1]);
                chartData[p]['series'][j].name = printableName(compareChampionsNames[champion]) + " " + chartData[p]['series'][j].origName;
                chartData[p]['series'][j].color = compareChampionsLineColors[champion];
                chartData[p]['series'][j].lineColor = compareChampionsLineColors[champion];
                chartData[p]['series'][j].fillColor = compareChampionsFillColors[champion];
                chartData[p]['series'][j].primarySeries = false;
                chartData[p]['series'][j].championName = printableName(compareChampionsNames[champion]);
                var newseries = $.extend(new chartData[p]['series'][j].constructor, chartData[p]['series'][j]);
                champion_chart['series'].splice((seriesCount)*(champion+2) + 1 + champion, 0, newseries);
                seriesCount += 1;
            }
            for(j in chartData[p]['yAxis']) {
                yAxiscount += 1;
            }
        }
    }
    
    console.log(champion_chart['series']);
    
    $("#champion_chart").height(chartHeight);
    
    $('#champion_chart').highcharts('StockChart', {
        rangeSelector : {
            buttons: [{ type: 'minute', count: '3', text: '3m'}, { type: 'minute', count: '10', text: '10m'}, {type : 'all', text : "All"}],
            inputEnabled: false
        },

        title : {
            enabled: 'false'
        },
        
        xAxis: {
            type : 'datetime',
            ordinal : false,
            gridLineWidth: 0,
            labels: { formatter: function () {
                var seconds = (this.value / 1000);
                var dispseconds = seconds % 60;
                if(dispseconds < 10) {
                    dispseconds = "0"+dispseconds;
                }
                var dispminutes = Math.floor(seconds / 60);
                return dispminutes+":"+dispseconds;
            }}
        },
        
        tooltip: {
            formatter: function() {
                var s = '<b>'+ Highcharts.dateFormat('%H:%M:%S', this.x) +'</b>';

                $.each(this.points, function(i, point) {
                    if(compareChampionsMode == true) {
                        var dispVal = Math.round(point.y);
                        if(this.series.tooltipOptions.valueDecimals > 0) {
                            var roundingFactor = Math.pow(10, this.series.tooltipOptions.valueDecimals);
                            dispVal = Math.round(point.y * roundingFactor) / roundingFactor;
                        }
                        dispVal = "<span style='color: "+this.series.options.color+"'>"+dispVal+"</span>";
                        if(this.series.options.primarySeries == true) {

                            
                            if(this.series.name.indexOf("is dead") > 0) {
                                s += '<br/><div class="chart_legend_series">Currently Dead:</div>&zwnj;';
                                if (point.y == 1) {
                                    s += dispVal.replace(">1<", ">"+printableName(this.series.options.championName)+"<");
                                }
                            }
                            else
                                s += '<br/><div class="chart_legend_series">'+ printableName(this.series.options.origName) + ":</div>" + this.series.options.championName + ": " + dispVal;
                        }
                        else {
                            if(this.series.name.indexOf("is dead") > 0) {
                                if (point.y == 1) {
                                    if(s.substr(-1) != ";")
                                        s += ", ";
                                    s += dispVal.replace(">1<", ">"+printableName(this.series.options.championName)+"<");
                                }
                            }
                            else
                                s += " | " + this.series.options.championName + ": " + dispVal;
                        }
                    }
                    else {
                        if(this.series.name.indexOf("is dead") > 0) {
                            if (point.y == 1) {
                                s += '<br/><strong style="color: #F33;">'+this.series.name+"</strong>";
                            }
                            else {
                                s += '<br/>'+this.series.name.replace("is dead", "is not dead");
                            }
                        }
                        else {
                            var dispVal = Math.round(point.y);
                            if(this.series.tooltipOptions.valueDecimals > 0) {
                                var roundingFactor = Math.pow(10, this.series.tooltipOptions.valueDecimals);
                                dispVal = Math.round(point.y * roundingFactor) / roundingFactor;
                            }
                            s += '<br/>'+ this.series.name + ": " + dispVal;
                        }
                    }
                });
            
                return s;
            },
            useHTML: true
        },
        
        plotOptions: {
            line : {
                dataGrouping: {"units" : [['second', [1, 5]]], "approximation": "open"}
            },
            area : {
                dataGrouping: {"units" : [['second', [1, 5]]], "approximation": "open"}
            },
        },
        
        yAxis: champion_chart['yAxis'],
        series : champion_chart['series'],
        
        navigator : {
            baseSeries: 0,
            color: "#000",
            fillColor: "#FFF",
            negativeColor: "#000",
            negativeFillColor: "#FFF",
            xAxis: { labels: { formatter: function () {
                var seconds = (this.value / 1000);
                var dispseconds = seconds % 60;
                if(dispseconds < 10) {
                    dispseconds = "0"+dispseconds;
                }
                var dispminutes = Math.floor(seconds / 60);
                return dispminutes+":"+dispseconds;
            }}}
        }
    });
}