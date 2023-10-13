import json
import plotly.graph_objects as go
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

# Load the JSON data from "d.json"
with open("d.json", "r") as json_file:
    data = json.load(json_file)

# Initialize lists to store the nodes and links for the Sankey diagram
nodes = []
links = []

# Create a dictionary to map proposal and choice to a unique target index
target_index_map = {}

# Define a color map for the choices
color_map = {1: "rgba(0, 128, 0, 0.4)",  # For with 40% transparency
             2: "rgba(255, 0, 0, 0.4)",  # Against with 40% transparency
             3: "rgba(128, 128, 128, 0.4)"}  # Abstain with 40% transparency

unique_titles = set()
unique_voters = set()

address_to_name = {
    "0x0eb5b03c0303f2f47cd81d7be4275af8ed347576": "TreasureDAO",
    "0x1b686ee8e31c5959d9f5bbd8122a58682788eead": "l2beatcom.eth",
    "0xf4b0556b9b6f53e00a1fdd2b0478ce841991d8fa": "olimpio.eth",
    "0x2ef27b114917dd53f8633440a7c0328fef132e2f": "0x2ef27b114917dd53f8633440a7c0328fef132e2f",
    "0xbbe98d590d7eb99f4a236587f2441826396053d3": "PlutusDAO",
    "0xf92f185abd9e00f56cb11b0b709029633d1e37b4": "0xf92f185abd9e00f56cb11b0b709029633d1e37b4",
    "0x683a4f9915d6216f73d6df50151725036bd26c02": "Gauntlet",
    "0x839395e20bbb182fa440d08f850e6c7a8f6f0780": "Griff Green 🌱🎗🌶👹",
    "0x190473b3071946df65306989972706a4c006a561": "ChainLinkGod",
    "0x8a3e9846df0cdc723c06e4f0c642ffff82b54610": "0x8a3e9846df0cdc723c06e4f0c642ffff82b54610",
    "0xe48c655276c23f1534ae2a87a2bf8a8a6585df70": "0xe48c655276c23f1534ae2a87a2bf8a8a6585df70",
    "0xa5df0cf3f95c6cd97d998b9d990a86864095d9b0": "Blockworks Research",
    "0x2e3bef6830ae84bb4225d318f9f61b6b88c147bf": "Camelot",
    "0x8f73be66ca8c79382f72139be03746343bf5faa0": "mihal.eth",
    "0xb5b069370ef24bc67f114e185d185063ce3479f8": "0xfrisson.eth",
    "0xdb5781a835b60110298ff7205d8ef9678ff1f800": "yoav.eth",
    "0x9808e45c613eba00ba18fb3d314dc4d4712c4a85": "0x9808e45c613eba00ba18fb3d314dc4d4712c4a85",
    "0x79c4213a328e3b4f1d87b4953c14759399db25e2": "litocoen",
    "0x18bf1a97744539a348304e9d266aac7d446a1582": "Princeton Blockchain Club",
    "0x978982772b8e4055b921bf9295c0d74eb36bc54e": "0x978982772b8e4055b921bf9295c0d74eb36bc54e"
}

# Iterate through the data to create nodes and links
for vote in data["data"]["votes"]:
    voter = address_to_name[vote["voter"].lower()]
    proposal = vote["proposal"]["title"]
    choice = vote["choice"]
    vp = vote["vp"]
    unique_titles.add(proposal)
    unique_voters.add(voter)

    # Create the voter node
    if voter not in nodes:
        nodes.append(voter)

    # Create the target node for the proposal and choice
    target_label = f"{proposal}"
    if target_label not in nodes:
        nodes.append(target_label)
        target_index_map[target_label] = len(nodes) - 1

    # Create a link from the voter to the target node with the assigned color
    links.append({
        "source": nodes.index(voter),
        "target": target_index_map[target_label],
        "value": vp,
        "color": color_map[choice]
    })

# Create the Sankey diagram
sankey_fig = go.Figure(go.Sankey(
    node=dict(
        pad=15,
        thickness=20,
        line=dict(color="black", width=0.5),
        label=nodes
    ),
    link=dict(
        source=[link["source"] for link in links],
        target=[link["target"] for link in links],
        value=[link["value"] for link in links],
        color=[link["color"] for link in links]
    )
))

app = dash.Dash(__name__)

# Create a list of unique proposals from the 'nodes' list
proposals  = list(unique_titles)
voterz  = list(unique_voters)


# Define the layout of the web application
app.layout = html.Div([
    dcc.Graph(id='sankey', figure=sankey_fig, style={'width': '100vw', 'height': '80vh'}),
    dcc.Checklist(
        id='choice-filter',
        options=[
            {'label': 'For', 'value': 1},
            {'label': 'Against', 'value': 2},
            {'label': 'Abstain', 'value': 3}
        ],
        value=[1, 2, 3],
        style={'display': 'inline-block'}
    ),
    dcc.Dropdown(
        id='proposal-filter',
        options=[{'label': proposal, 'value': proposal} for proposal in proposals],
        multi=True, 
#        style={'display': 'inline-block'}
    ),
    dcc.Dropdown(
        id='voter-filter',
        options=[{'label': voter, 'value': voter} for voter in voterz],
        multi=True,
#        style={'display': 'inline-block'}
    )
])

# Define callback to update Sankey diagram based on choice and proposal filters
@app.callback(
    Output('sankey', 'figure'),
    Input('choice-filter', 'value'),
    Input('proposal-filter', 'value'),
    Input('voter-filter', 'value')
)
def update_sankey(choice_filter, proposal_filter, voter_filter):
    # Filter links by choice
    filtered_links = [link for link in links if link["color"] in [color_map[c] for c in choice_filter]]
    
    # Filter links by proposal
    if proposal_filter:
        filtered_links = [link for link in filtered_links if nodes[link["target"]] in proposal_filter]

    # Filter links by voter
    if voter_filter:
        filtered_links = [link for link in filtered_links if nodes[link["source"]] in voter_filter]

    filtered_fig = go.Figure(go.Sankey(
        node=sankey_fig['data'][0]['node'],  # Use the same node configuration
        link=dict(
            source=[link["source"] for link in filtered_links],
            target=[link["target"] for link in filtered_links],
            value=[link["value"] for link in filtered_links],
            color=[link["color"] for link in filtered_links]
        )
    ))
    return filtered_fig

if __name__ == '__main__':
    app.run_server(debug=True)

