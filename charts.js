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
    selectedChampion = $("#champion_chart_selector").val().split("_");
    selectedChampionName = data['playerData'][selectedChampion[0]][selectedChampion[1]]['champion'];

    //Output champion details
    
    
    //Draw history chart
    chartData = {
        "championGoldHistory" : {
            series : [
                {
                    name : selectedChampionName + " gold",
                    data : convertDataTime(convertHashToArray(data['gold'][selectedChampion[0]][selectedChampion[1]]['total'])),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#333",
                    color: "#333"
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
                    name : selectedChampionName + " gpm (last 1 min.)",
                    data : convertDataTime(convertHashToArray(data['gold'][selectedChampion[0]][selectedChampion[1]]['gpm1'])),
                    tooltip: {
                        valueDecimals: 2
                    },
                    lineColor: "#DDD",
                    color: "#DDD"
                },
                {
                    name : selectedChampionName + " gpm (last 5 min.)",
                    data : convertDataTime(convertHashToArray(data['gold'][selectedChampion[0]][selectedChampion[1]]['gpm5'])),
                    tooltip: {
                        valueDecimals: 2
                    },
                    lineColor: "#888",
                    color: "#888"
                },
                {
                    name : selectedChampionName + " gpm (cumulative)",
                    data : convertDataTime(convertHashToArray(data['gold'][selectedChampion[0]][selectedChampion[1]]['gpm'])),
                    tooltip: {
                        valueDecimals: 2
                    },
                    lineColor: "#333",
                    color: "#333"
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
                    name : selectedChampionName + " creep score",
                    data : convertDataTime(convertHashToArray(data['objectives'][selectedChampion[0]][selectedChampion[1]]['minions'])),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#333",
                    color: "#333"
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
                    name : selectedChampionName + " is dead",
                    type : 'area',
                    step : 'true',
                    data : convertDataTime(convertHashToArray(data['kda'][selectedChampion[0]][selectedChampion[1]]['is_dead'])),
                    tooltip: {
                        valueDecimals: 0
                    },
                    lineColor: "#333",
                    lineWidth: 0,
                    fillColor: "#999",
                    color: "#333"
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
            if(chartData[p]['series'][j].yAxisOffset)
                chartData[p]['series'][j].yAxis = parseInt(chartData[p]['series'][j].yAxisOffset) + parseInt(yAxiscount);
            else
                chartData[p]['series'][j].yAxis = parseInt(yAxiscount);
            champion_chart['series'].push(chartData[p]['series'][j]);
        }
        
        for(j in chartData[p]['yAxis']) {
            chartData[p]['yAxis'][j].top = chartHeight - 85;
            champion_chart['yAxis'].push(chartData[p]['yAxis'][j]);
            chartHeight += chartData[p]['yAxis'][j]['height'] + 10;
            yAxiscount += 1;
        }
    }
    
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
                    var dispVal = Math.round(point.y);
                    if(this.series.tooltipOptions.valueDecimals > 0) {
                        var roundingFactor = Math.pow(10, this.series.tooltipOptions.valueDecimals);
                        dispVal = Math.round(point.y * roundingFactor) / roundingFactor;
                    }
                    s += '<br/>'+ this.series.name + ": " + dispVal;
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