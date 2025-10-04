let svg, width, height, simulation, linkGroup, nodeGroup, labelGroup;
let graph = { nodes: [], edges: [] };
let stepIndex = 0;
let animationInterval = null;

document.addEventListener("DOMContentLoaded", () => {
  svg = d3.select("#network")
    .attr("width", window.innerWidth * 0.6)
    .attr("height", window.innerHeight);

  width = +svg.attr("width");
  height = +svg.attr("height");

  linkGroup = svg.append("g").attr("class", "links");
  nodeGroup = svg.append("g").attr("class", "nodes");
  labelGroup = svg.append("g").attr("class", "labels");

  // Forms
  document.getElementById("routerForm").addEventListener("submit", e => {
    e.preventDefault();
    addRouter();
  });

  document.getElementById("linkForm").addEventListener("submit", e => {
    e.preventDefault();
    addLink();
  });

  document.getElementById("simulateBtn").addEventListener("click", () => {
    let protocol = document.getElementById("protocol").value;
    fetchAnimate(protocol);
  });

  document.getElementById("exportBtn").addEventListener("click", exportTopology);
  document.getElementById("importBtn").addEventListener("click", importTopology);
  document.getElementById("clearBtn").addEventListener("click", clearTopology);
});

// ---- TOPOLOGY BUILDER ----
function addRouter() {
  let id = document.getElementById("routerId").value;
  let ip = document.getElementById("routerIp").value;

  if (!id || !ip) return;

  graph.nodes.push({ id: id, ip: ip });
  updateNodeDropdowns();
  updateGraph();

  document.getElementById("routerForm").reset();
}

function addLink() {
  let src = document.getElementById("linkSource").value;
  let dst = document.getElementById("linkTarget").value;
  let cost = parseInt(document.getElementById("linkCost").value);

  if (!src || !dst || src === dst) return;

  graph.edges.push({ source: src, target: dst, cost: cost });
  updateGraph();

  document.getElementById("linkForm").reset();
  updateNodeDropdowns();
}

function updateNodeDropdowns() {
  let dropdowns = [document.getElementById("linkSource"), document.getElementById("linkTarget")];
  dropdowns.forEach(dd => {
    dd.innerHTML = "";
    graph.nodes.forEach(n => {
      let opt = document.createElement("option");
      opt.value = n.id;
      opt.textContent = n.id;
      dd.appendChild(opt);
    });
  });
}

// ---- TOPOLOGY EXPORT/IMPORT ----
function exportTopology() {
  let json = JSON.stringify(graph, null, 2);
  console.log(json);
  alert("Topology exported to console.");
}

function importTopology() {
  let json = prompt("Paste topology JSON:");
  if (json) {
    graph = JSON.parse(json);
    updateGraph();
    updateNodeDropdowns();
  }
}

function clearTopology() {
  graph = { nodes: [], edges: [] };
  updateGraph();
  updateNodeDropdowns();
}

// ---- SIMULATION ----
function fetchAnimate(protocol) {
  stopAnimation(); // Stop any previous animation
  clearLog();      // Clear previous simulation logs

  // Send current graph topology to backend
  fetch("/add_topology", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(graph)
  })
  .then(res => res.json())
  .then(() => {
    // Request animation steps from backend
    fetch("/animate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ protocol: protocol })
    })
    .then(res => res.json())
    .then(data => {
      console.log("Animate steps received:", data.steps); // Debug

      if (data.steps && data.steps.length > 0) {
        stepIndex = 0;
        animateSteps(data.steps); // Start animating steps
      } else {
        alert("No steps returned from simulation. Check your topology or algorithm.");
      }
    })
    .catch(err => {
      console.error("Error fetching animation steps:", err);
      alert("Failed to simulate routing. See console for details.");
    });
  })
  .catch(err => {
    console.error("Error sending topology:", err);
    alert("Failed to send topology to server. See console for details.");
  });
}

// Utility: clear simulation log
function clearLog() {
  let log = document.getElementById("log");
  log.innerHTML = "";
}


function animateSteps(steps) {
  animationInterval = setInterval(() => {
    if (stepIndex >= steps.length) {
      stopAnimation();
      return;
    }

    let step = steps[stepIndex];
    updateGraph(step);

    let log = document.getElementById("log");
    let li = document.createElement("li");
    li.textContent = `Step ${stepIndex + 1}: ${JSON.stringify(step.update || "Update")}`;
    log.appendChild(li);

    stepIndex++;
  }, 1200);
}

function stopAnimation() {
  if (animationInterval) {
    clearInterval(animationInterval);
    animationInterval = null;
  }
}

// ---- D3 GRAPH RENDER ----
function updateGraph(step = null) {
  let nodesData = step ? step.nodes.map(d => ({ id: d[0], ...d[1] })) : graph.nodes;
  let edgesData = step ? step.edges.map(d => ({ ...d })) : graph.edges;

  // Map source/target strings to node objects
  let edges = edgesData.map(e => ({
    source: nodesData.find(n => n.id === e.source),
    target: nodesData.find(n => n.id === e.target),
    cost: e.cost
  }));

  // --- D3 links ---
  let linkElems = linkGroup.selectAll("line").data(edges, d => d.source.id + "-" + d.target.id);
  linkElems.exit().remove();
  linkElems.enter().append("line")
    .attr("stroke", "#aaa")
    .attr("stroke-width", 2)
    .merge(linkElems)
    .transition().duration(800)
    .attr("stroke", "#4CAF50");

  // --- D3 nodes ---
  let nodeElems = nodeGroup.selectAll("circle").data(nodesData, d => d.id);
  nodeElems.exit().remove();
  nodeElems.enter().append("circle")
    .attr("r", 18)
    .attr("fill", "#2196F3")
    .attr("stroke", "#fff")
    .attr("stroke-width", 2)
    .call(drag(simulation))
    .merge(nodeElems);

  // --- D3 labels ---
  let labels = labelGroup.selectAll("text").data(nodesData, d => d.id);
  labels.exit().remove();
  labels.enter().append("text")
    .attr("dy", 4)
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .attr("fill", "#fff")
    .text(d => d.id)
    .merge(labels)
    .text(d => d.id);

  // --- Link labels ---
  let linkLabels = linkGroup.selectAll("text").data(edges, d => d.source.id + "-" + d.target.id);
  linkLabels.exit().remove();
  linkLabels.enter()
    .append("text")
    .attr("text-anchor", "middle")
    .attr("font-size", "12px")
    .attr("fill", "#000")
    .merge(linkLabels)
    .text(d => d.cost);
  
  // --- D3 simulation ---
  simulation = d3.forceSimulation(nodesData)
    .force("link", d3.forceLink(edges).id(d => d.id).distance(150))
    .force("charge", d3.forceManyBody().strength(-500))
    .force("center", d3.forceCenter(width / 2, height / 2));

  simulation.on("tick", () => {
    linkGroup.selectAll("line")
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);

    nodeGroup.selectAll("circle")
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);

    labelGroup.selectAll("text")
      .attr("x", d => d.x)
      .attr("y", d => d.y);

    linkGroup.selectAll("text")
    .attr("x", d => (d.source.x + d.target.x) / 2)
    .attr("y", d => (d.source.y + d.target.y) / 2);
  });
}

function drag(sim) {
  function dragstarted(event, d) {
    if (!event.active) sim.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  }
  function dragged(event, d) {
    d.fx = event.x;
    d.fy = event.y;
  }
  function dragended(event, d) {
    if (!event.active) sim.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  }
  return d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended);
}
