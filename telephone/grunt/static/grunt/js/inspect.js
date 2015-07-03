function visualize(chain) {
  chain = JSON.parse(chain); // shouldn't have to do this!
  globalVars.chain = chain;
  globalVars.messages = messages;

  var messages = chain.messages,
      numBranches = chain.branches,
      numGenerations = chain.generations;

  var widthPerBranch = 160,
      heightPerGeneration = 120;

  var circleSize = 40;

  var maxTextWidth = 20,     // how far will the text stick out on the right side of the nodes?
      textHorizontal = 25,   // text x relative to node x
      textVertical = -10,    // text y relative to node y
      textBuffer = 15;       // text y relative to other text ys

  // Layout
  var tree = d3.layout.tree(),  // for laying out the nodes on the page
      link = d3.svg.diagonal(); // for connecting the nodes on the page

  var treeSize = [numBranches * widthPerBranch, numGenerations * heightPerGeneration];

  tree
    .size(treeSize)
    .children(function (message) { return message.children; });

  link
    .projection(function (message) { return [message.x, message.y + circleSize]; })

  var svg = d3.select("svg");

  // Clear the previous chain
  svg
    .selectAll("g")
    .remove();

  svg
    .selectAll("path")
    .remove();

  // Adjust the size of the svg element
  var svgWidth = treeSize[0] + maxTextWidth,
      svgHeight = treeSize[1] + circleSize * 2;
  svg
    .attr("width", svgWidth)
    .attr("height", svgHeight)

  // Bind the message data into g elements
  svg
    .selectAll("g.message")
    .data(tree(messages))
    .enter()
    .append("g")
    .attr("class", function (message) {
      var type = message.audio ? "filled" : "empty";
      return "message " + type;
    })
    .attr("transform", function (message) {
      return "translate(0," + circleSize + ")";
    });

  // Add the links
  svg
    .selectAll("path")
    .data(tree.links(tree(messages)))
    .enter().insert("path","g")
    .attr("d", link)
    .style("fill", "none")
    .style("stroke", "black")
    .style("stroke-width", "2px");

  var messages = svg.selectAll("g.message");

  // Create a circle for each message
  messages
    .append("circle")
    .attr("r", 20)
    .attr("cx", function (message) { return message.x; })
    .attr("cy", function (message) { return message.y; })

  // Label each circle
  messages
    .append("text")
    .attr("class", "label")
    .text(function (message) { return message.pk; })
    .attr("x", function (message) { return message.x; })
    .attr("y", function (message) { return message.y; })
    .attr("text-anchor", "middle")
    .attr("dy", ".35em")
    .style("pointer-events", "none")

  var filled = svg.selectAll("g.filled")

  // Add play button
  filled
    .append("text")
    .attr("class", "play")
    .attr("x", function (message) { return message.x + textHorizontal; })
    .attr("y", function (message) { return message.y + textVertical; })
    .text("play")
    .on("click", function (message) {
      $("audio").attr("src", message.audio);
      $("audio").trigger("play");
    });

  // Add split button
  filled
    .append("text")
    .attr("class", "split")
    .attr("x", function (message) { return message.x + textHorizontal; })
    .attr("y", function (message) { return message.y + textVertical + textBuffer; })
    .text("split")
    .on("click", function (message) {
      $.post(message.sprout_url,
        {csrfmiddlewaretoken: csrf_token},
        function (data) { visualize(data); }
      );
    });

  // Add download button
  filled
    .append("text")
    .attr("class", "split")
    .attr("x", function (message) { return message.x + textHorizontal; })
    .attr("y", function (message) { return message.y + textVertical + 2 * textBuffer; })
    .text("download")
    .on("click", function (message) {
      var link = document.createElement("a");
      link.download = message.audio;
      link.href = message.audio;
      link.click();
    });

  var empty = svg.selectAll("g.empty");

  // Add upload button
  empty
    .append("text")
    .attr("class", "upload")
    .attr("x", function (message) { return message.x + textHorizontal; })
    .attr("y", function (message) { return message.y + textVertical; })
    .text("upload")
    .on("click", function (message) {
      window.location.href = message.upload_url;
    })

  // Add delete button
  empty
    .append("text")
    .attr("class", "delete")
    .attr("x", function (message) { return message.x + textHorizontal; })
    .attr("y", function (message) { return message.y + textVertical + textBuffer; })
    .text("delete")
    .on("click", function (message) {
      $.post(message.close_url,
        {csrfmiddlewaretoken: csrf_token},
        function (data) { visualize(data); }
      );
    })

  var nodes = messages.selectAll("circle");

  // Make clicking the nodes toggle their "active" class
  nodes
    .on("click", function (message) {
      var circle = d3.select(this);
      circle.classed("active", !circle.classed("active"));
    });

}
