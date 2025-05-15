document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const csvFileInput = document.getElementById('csvFile');
    const loadingDiv = document.getElementById('loading');
    const errorDiv = document.getElementById('error');
    const cyContainer = document.getElementById('cy');
    const nodeInfoPanel = document.getElementById('node-info');
    const pathListElement = document.getElementById('path-list');

    let cy = null; // Variable to hold the Cytoscape instance

    uploadForm.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission

        const file = csvFileInput.files[0];
        if (!file) {
            alert('Please select a CSV file.');
            return;
        }

        // Show loading, hide error
        const formData = new FormData();
        formData.append('file', file);
        loadingDiv.classList.remove('hidden');
        errorDiv.classList.add('hidden');
        errorDiv.textContent = ''; // Clear previous errors
        nodeInfoPanel.textContent = 'Click on a node to see details.'; // Reset details
        pathListElement.innerHTML = ''; // Clear previous paths


        

        try {
            // Send the file to the backend
            console.log("Sending to backend.")
            const response = await fetch('http://localhost:5000/upload', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }

            const results = await response.json();
            console.log('Analysis Results:', results);

            // Initialize Cytoscape.js with the graph data
            initializeGraph(results.nodes, results.edges);

            // Populate the sidebar with risky paths
            displayRiskyPaths(results.risky_paths);


        } catch (error) {
            console.error('Error during analysis:', error);
            errorDiv.textContent = `Analysis failed: ${error.message}`;
            errorDiv.classList.remove('hidden');
             // Clear graph if exists
            if (cy) {
                 cy.destroy();
                 cy = null;
            }
             cyContainer.innerHTML = ''; // Clear Cytoscape container content
             pathListElement.innerHTML = '<li>Error loading paths.</li>';


        } finally {
            // Hide loading
            loadingDiv.classList.add('hidden');
        }
    });

    function initializeGraph(nodesData, edgesData) {
        if (cy) {
            cy.destroy(); // Destroy existing graph if any
        }

        // Map nodes and edges to Cytoscape.js format
        const elements = [];

        nodesData.forEach(node => {
            elements.push({
                data: {
                    id: node.id, // Use original ID as node ID
                    label: node.label,
                    type: node.type,
                    anomaly_score: node.anomaly_score,
                    prediction: node.prediction,
                    full_data: node // Store all data for details panel
                }
            });
        });

        edgesData.forEach(edge => {
            elements.push({
                data: {
                    source: edge.source,
                    target: edge.target,
                    label: edge.relationship_type || '', // Use relationship type as label
                    relationship_type: edge.relationship_type
                }
            });
        });


        cy = cytoscape({
            container: cyContainer, // container to render in
            elements: elements,
            layout: {
                name: 'cose', // or 'circle', 'grid', 'breadthfirst', etc. 'cose' is good for general graphs
                animate: true,
                animationDuration: 500,
                padding: 10
            },
            style: [ // Graph styling
                {
                    selector: 'node',
                    style: {
                        'label': 'data(label)',
                        'text-valign': 'bottom',
                        'text-halign': 'center',
                        'font-size': '10px',
                        'padding': '5px',
                         'border-width': 1,
                         'border-color': '#ccc',
                         'background-color': '#666', // Default color
                         'width': '20px',
                         'height': '20px',
                    }
                },
                {
                    selector: 'edge',
                    style: {
                        'width': 1,
                        'line-color': '#ccc',
                        'target-arrow-color': '#ccc',
                        'target-arrow-shape': 'triangle',
                        'curve-style': 'bezier', // or 'haystack' for performance on large graphs
                        'label': 'data(label)', // Show edge type
                        'font-size': '8px',
                        'text-rotation': 'autorotate',
                        'color': '#555'
                    }
                },

                // --- Node Type Specific Styles ---
                { selector: 'node[type="user"]', style: { 'background-color': '#3498db', 'shape': 'ellipse' } },
                { selector: 'node[type="resource"]', style: { 'background-color': '#2ecc71', 'shape': 'rectangle' } },
                { selector: 'node[type="config"]', style: { 'background-color': '#f39c12', 'shape': 'diamond' } },
                // Add more types as needed...

                // --- Anomaly Specific Styles ---
                {
                     selector: 'node[prediction = -1]', // Nodes predicted as anomalous by Isolation Forest
                     style: {
                         'border-color': '#e74c3c', // Red border
                         'border-width': 3,
                          'shadow-blur': 10,
                          'shadow-color': '#e74c3c',
                          'shadow-opacity': 0.5,
                     }
                 },
                // You could add color intensity based on anomaly_score if you wanted

            ],
            wheelSensitivity: 0.2 // Make zooming less sensitive
        });

        // Add event listener for node clicks
        cy.on('tap', 'node', (event) => {
            const node = event.target;
            const nodeData = node.data('full_data'); // Retrieve stored full data

            let detailsHtml = `
                <p><strong>ID:</strong> ${nodeData.id}</p>
                <p><strong>Type:</strong> ${nodeData.type}</p>
                <p><strong>Anomaly Score:</strong> ${nodeData.anomaly_score !== null ? nodeData.anomaly_score.toFixed(4) : 'N/A'}</p>
                <p><strong>Prediction:</strong> ${nodeData.prediction !== null ? (nodeData.prediction === -1 ? 'Anomaly (-1)' : 'Inlier (1)') : 'N/A'}</p>
                <p><strong>Internal Index:</strong> ${nodeData.node_index}</p>
            `;
            // Optionally add features, maybe format them nicely
             if (nodeData.features && nodeData.features.length > 1) { // Skip the type feature
                 detailsHtml += `<p><strong>Features:</strong> ${nodeData.features.slice(1).map(f => f.toFixed(2)).join(', ')}</p>`;
             }


            nodeInfoPanel.innerHTML = detailsHtml;
        });

         // Optional: Clear node details when clicking on the background
         cy.on('tap', (event) => {
            if (event.target === cy) { // If click was on the background
                 nodeInfoPanel.textContent = 'Click on a node to see details.';
            }
         });

         // Fit graph to view after layout is done
         cy.ready(function(){
             cy.fit(cy.elements(), 50); // fit to all elements with 50px padding
         });

    }

    function displayRiskyPaths(paths) {
        pathListElement.innerHTML = ''; // Clear previous list
        if (paths.length === 0) {
            pathListElement.innerHTML = '<li>No risky paths found (within limits).</li>';
            return;
        }

        paths.forEach((path, index) => {
            const listItem = document.createElement('li');
            // Using path_with_types for clearer display including node types
            listItem.innerHTML = `<strong>Rank ${index + 1}</strong> (Score: ${path.score.toFixed(4)})<br>${path.path_with_types}`;

            // Optional: Add interaction to highlight path on graph when clicking list item
            // This would require adding classes/styles in Cytoscape and getting path elements
            listItem.addEventListener('click', () => {
                console.log("Path clicked:", path.path_ids);
                // Remove previous highlights
                cy.$('.highlighted-path').removeClass('highlighted-path');
                cy.elements().removeClass('highlighted-node').removeClass('faded');

                // Highlight nodes and edges in this path
                let currentCollection = cy.collection();
                for (let i = 0; i < path.path_ids.length; i++) {
                     const nodeId = path.path_ids[i];
                     const nodeElement = cy.$id(nodeId);
                     currentCollection = currentCollection.union(nodeElement);

                     if (i < path.path_ids.length - 1) {
                          const nextNodeId = path.path_ids[i+1];
                          // Find the edge between current and next node
                          const edgeElement = nodeElement.edgesTo(`[id="${nextNodeId}"]`); // This might need refinement if multiple edges exist
                          currentCollection = currentCollection.union(edgeElement);
                     }
                }

                // Apply highlight styles
                currentCollection.addClass('highlighted-path');

                // Fade other elements
                 cy.elements().difference(currentCollection).addClass('faded');

            });


            pathListElement.appendChild(listItem);
        });

         // Add styles for highlighting in Cytoscape
         cy.style()
            .selector('.highlighted-path')
            .style({
                 'line-color': '#f00',
                 'target-arrow-color': '#f00',
                 'width': 3,
                 'opacity': 1,
                 'z-index': 999 // Bring highlighted elements to front
            })
            .selector('.highlighted-path:parent') // If using compound nodes
            .style({
                 'border-color': '#f00',
            })
             .selector('.highlighted-node') // Style for highlighted nodes
             .style({
                  'border-color': '#f00',
                  'border-width': 3,
                  'z-index': 1000,
                  'opacity': 1
             })
             .selector('.faded')
             .style({
                  'opacity': 0.3
             })
         .update(); // Apply the new style
    }

    // Initial state: Hide loading and error
    loadingDiv.classList.add('hidden');
    errorDiv.classList.add('hidden');

});