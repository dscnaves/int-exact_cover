import networkx as nx
import pandas as pd
import matplotlib
# Use a non-interactive backend ('Agg') to prevent pop-up window errors
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import os

def draw_graph_from_csv():
    """
    Reads edge data from a CSV file and saves a directed graph image.
    
    Assumes this script is in 'int-exact_cover/src/utils/' and the CSV
    is in 'int-exact_cover/results/py_parsed_data/'.
    
    The resulting graph image will be saved in 
    'int-exact_cover/results/plots/graph.png'.
    """
    
    # --- 1. Define File Paths ---
    # Get the directory where this script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the input CSV
    csv_path = os.path.join(
        base_dir, 
        '..', '..', 'results', 'py_parsed_data', 'edges.csv'
    )
    
    # Path for the output plot
    output_plot_dir = os.path.join(
        base_dir, 
        '..', '..', 'results', 'plots'
    )
    output_plot_path = os.path.join(output_plot_dir, 'graph.png')
    
    # Normalize paths to clean them up (e.g., remove '..' parts)
    csv_path = os.path.normpath(csv_path)
    output_plot_path = os.path.normpath(output_plot_path)

    print(f"Attempting to read CSV from: {csv_path}")

    # --- 2. Check if CSV File Exists ---
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Please run the 'create_csv.py' script first.")
        return

    # --- 3. Create Output Directory ---
    # Ensure the 'results/plots' directory exists before saving
    try:
        os.makedirs(os.path.dirname(output_plot_path), exist_ok=True)
    except OSError as e:
        print(f"Error creating directory {os.path.dirname(output_plot_path)}: {e}")
        return

    # --- 4. Load Data and Create Graph ---
    try:
        # Read the CSV file using pandas
        df = pd.read_csv(csv_path)
        
        # Ensure columns are read as strings to be safe
        df['origem'] = df['origem'].astype(str)
        df['destino'] = df['destino'].astype(str)

        # Create a directed graph (DiGraph) from the dataframe
        G = nx.from_pandas_edgelist(
            df, 
            source='origem', 
            target='destino', 
            create_using=nx.DiGraph()
        )

        print(f"Graph created with {G.number_of_nodes()} nodes and {G.number_of_edges()} edges.")

        # --- 5. Draw the Graph ---
        plt.figure(figsize=(12, 12))
        
        # Use a layout for better node spacing
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        nx.draw(
            G, 
            pos,
            with_labels=True, 
            node_color='skyblue', 
            node_size=700,
            edge_color='gray',
            font_size=10,
            font_weight='bold',
            arrows=True,
            arrowstyle='->',
            arrowsize=15
        )
        
        plt.title("Graph from edges.csv")
        
        # --- 6. Save the Graph to a File ---
        # This replaces plt.show()
        plt.savefig(output_plot_path)
        print(f"Graph successfully saved to: {output_plot_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    draw_graph_from_csv()