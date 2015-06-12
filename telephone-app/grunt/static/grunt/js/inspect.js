function tree(nodes) {
  var nodeById = {};

  // Index the nodes by id, in case they come out of order.
  nodes.forEach(function(d) {
  nodeById[d.pk] = d;
  });

  // Lazily compute children.
  nodes.forEach(function(d) {
  if (d.parent) {
    var parent = nodeById[d.parent];
    if (parent.children) parent.children.push(d);
    else parent.children = [d];
  }
  });

  return nodes[0];
}

function visualize(incData) {
  incData = JSON.parse(incData);

  rawData = incData;

  var firstChain = incData[0];

  nestedMessages = tree(firstChain.messages);

  var generationScale = d3.scale.category10([1,2,3,4]);

  treeChart = d3.layout.tree();
  treeChart.size([500, 500])
    .children(function(d) { return d.children });

  var bumpDown = 40;

  var linkGenerator = d3.svg.diagonal();
  linkGenerator
    .projection(function (d) {return [d.x, d.y+bumpDown]})

  // Make a g-element for every chain in the game
  // Right now, assumes a single chain
  d3.select("svg")
    .append("g")
    .attr("class", "chain")

  d3.select("g.chain").selectAll("g") // assumes single chain
    .data(treeChart(nestedMessages))
    .enter()
    .append("g")
    .attr("class", function(d) {
      var type = d.audio ? "filled" : "empty";
      return "message " + type;
    })
    .attr("transform", function(d) {
      return "translate(" +d.x+","+(d.y+bumpDown)+")"
    });

  d3.selectAll("g.message")
    .append("circle")
    .attr("r", 10);

  var bumpTextsRight = 15,
    bumpTextsDown = 5;

  playMessage = function(message) {
    $("audio").attr("src", message.audio);
    $("audio").trigger("play");
  }

  navToUploadPage = function(message) {
    window.location.href = message.upload_url
  }

  d3.selectAll("g.message")
    .append("g")
    .attr("transform", function(d) {
      return "translate(" + bumpTextsRight + "," + bumpTextsDown + ")";
    })
    .append("text")
    .text(function(el) { return el.audio ? "play" : "upload"; })
    .attr("class", function(el) { return el.audio ? "play" : "upload"; })
    .on("click", function(el) { return el.audio ? playMessage(el) : navToUploadPage(el); })

  splitChain = function(message) {
    $.post(message.sprout_url, {csrfmiddlewaretoken: csrf_token}, function() {
      window.location.reload();
    });
  }

  closeBranch = function(message) {
    $.post(message.close_url, {csrfmiddlewaretoken: csrf_token}, function() {
      window.location.reload();
    });
  }

  d3.selectAll("g.message")
    .append("g")
    .attr("transform", function(d) {
      return "translate(" + bumpTextsRight + "," + bumpTextsDown * 4 + ")";
    })
    .append("text")
    .text(function(el) { return el.audio ? "split" : "close"; })
    .attr("class", function(el) { return el.audio ? "split" : "close"; })
    .on("click", function(el) { return el.audio ? splitChain(el) : closeBranch(el); })

  d3.select("g.chain").selectAll("path")
    .data(treeChart.links(treeChart(nestedMessages)))
    .enter().insert("path","g")
    .attr("d", linkGenerator)
    .style("fill", "none")
    .style("stroke", "black")
    .style("stroke-width", "2px");

}
