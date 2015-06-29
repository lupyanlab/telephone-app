
function playMessage(message) {
  $("audio").attr("src", message.audio);
  $("audio").trigger("play");
}

function navToUploadPage(message) {
  window.location.href = message.upload_url
}

function splitChain(message) {
  $.post(message.sprout_url,
    {csrfmiddlewaretoken: csrf_token},
    function (data) { visualize(data); }
  );
}

function deleteBranch(message) {
  $.post(message.close_url,
    {csrfmiddlewaretoken: csrf_token},
    function (data) { visualize(data); }
  );
}

function visualize(chain) {
  chain = JSON.parse(chain);

  var nestedMessages = chain.messages;

  var maxWidth = 5,
      widthPerChain = 120,
      maxDepth = 4,
      heightPerGeneration = 200;

  var svgWidth = maxWidth * widthPerChain,
      svgHeight = maxDepth * heightPerGeneration;

  var bumpDown = 40;
  var circleSize = 40;

  treeChart = d3.layout.tree();
  treeChart.size([svgWidth, svgHeight-(2*bumpDown)])
    .children(function(d) { return d.children });

  var linkGenerator = d3.svg.diagonal()
    .projection(function (d) {return [d.x, d.y+bumpDown]})

  var bumpTextsRight = 26,
      bumpTextsDown = -5,
      buttonGutter = 20;

  var containerWidth = parseFloat(d3.select("div.container").style("max-width"));
  if (containerWidth < svgWidth) {
    d3.select("div.container").style("max-width", (svgWidth + 2*bumpDown + bumpTextsRight) + "px");
  }

  var svg = d3.select("svg");

  // Clear the previous chain
  svg
    .selectAll("g")
    .remove();

  svg
    .selectAll("path")
    .remove();

  // Adjust the size of the svg element
  svg
    .attr("width", svgWidth + bumpTextsRight)
    .attr("height", svgHeight)

  // Bind the message data into g elements
  svg
    .selectAll("g.message")
    .data(treeChart(nestedMessages))
    .enter()
    .append("g")
    .attr("class", function (message) {
      var type = message.audio ? "filled" : "empty";
      return "message " + type;
    })
    .attr("transform", function (message) {
      return "translate(0," + circleSize + ")";
    });

  var messages = svg.selectAll("g.message");

  // Create a circle for each message
  messages
    .append("circle")
    .attr("r", 20)
    .attr("cx", function (message) { return message.x; })
    .attr("cy", function (message) { return message.y; })

  // Add the links
  svg
    .selectAll("path")
    .data(treeChart.links(treeChart(nestedMessages)))
    .enter().insert("path","g")
    .attr("d", linkGenerator)
    .style("fill", "none")
    .style("stroke", "black")
    .style("stroke-width", "2px");

  // Label each circle
  messages
    .append("text")
    .text(function (message) { return message.pk; })
    .attr("x", function (message) { return message.x; })
    .attr("y", function (message) { return message.y; })
    .attr("text-anchor", "middle")
    .attr("dy", ".35em")
    .style("fill", function (message) {
      return message.audio ? "white" : "black";
    });

  messages
    .append("g")
    .attr("transform", function(d) {
      return "translate(" + bumpTextsRight + "," + bumpTextsDown + ")";
    })
    .append("text")
    .text(function(el) { return el.audio ? "play" : "upload"; })
    .attr("class", function(el) { return el.audio ? "play" : "upload"; })
    .on("click", function(el) { return el.audio ? playMessage(el) : navToUploadPage(el); })

  messages
    .append("g")
    .attr("transform", function(d) {
      return "translate(" + bumpTextsRight + "," + (bumpTextsDown + buttonGutter) + ")";
    })
    .append("text")
    .text(function(el) { return el.audio ? "split" : "close"; })
    .attr("class", function(el) { return el.audio ? "split" : "delete"; })
    .on("click", function(el) { return el.audio ? splitChain(el) : deleteBranch(el); })

  d3.selectAll("text")
    .on("mouseover", function () {
      d3.select(this).classed("active", true);
    })
    .on("mouseout", function () {
      d3.select(this).classed("active", false);
    });
}
