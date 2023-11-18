import json
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output, callback, clientside_callback, ClientsideFunction, page_container

# json of finished stip votes, use graphql api for live/other stuff
with open("d.json", "r") as json_file:
    data = json.load(json_file)

nodes = []
links = []

target_index_map = {}

color_map = {1: "rgba(0, 128, 0, 0.4)",  # For 
             2: "rgba(255, 0, 0, 0.4)",  # Against 
             3: "rgba(128, 128, 128, 0.4)"}  # Abstainmk

unique_titles = set()
unique_voters = set()

address_to_name = {
    "0x0eb5b03c0303f2f47cd81d7be4275af8ed347576": "TreasureDAO",
    "0x1b686ee8e31c5959d9f5bbd8122a58682788eead": "l2beatcom.eth",
    "0xf4b0556b9b6f53e00a1fdd2b0478ce841991d8fa": "olimpio.eth",
    "0x2ef27b114917dd53f8633440a7c0328fef132e2f": "MUX DAO",
    "0xbbe98d590d7eb99f4a236587f2441826396053d3": "PlutusDAO",
    "0xf92f185abd9e00f56cb11b0b709029633d1e37b4": "coinflipcanada",
    "0x683a4f9915d6216f73d6df50151725036bd26c02": "Gauntlet",
    "0x839395e20bbb182fa440d08f850e6c7a8f6f0780": "Griff Green",
    "0x190473b3071946df65306989972706a4c006a561": "ChainLinkGod",
    "0x8a3e9846df0cdc723c06e4f0c642ffff82b54610": "0x8a3e....4610",
    "0xe48c655276c23f1534ae2a87a2bf8a8a6585df70": "ercwl.eth",
    "0xa5df0cf3f95c6cd97d998b9d990a86864095d9b0": "Blockworks Research",
    "0x2e3bef6830ae84bb4225d318f9f61b6b88c147bf": "Camelot",
    "0x8f73be66ca8c79382f72139be03746343bf5faa0": "mihal.eth",
    "0xb5b069370ef24bc67f114e185d185063ce3479f8": "0xfrisson.eth",
    "0xdb5781a835b60110298ff7205d8ef9678ff1f800": "yoav.eth",
    "0x9808e45c613eba00ba18fb3d314dc4d4712c4a85": "0x9808...4a85",
    "0x79c4213a328e3b4f1d87b4953c14759399db25e2": "litocoen",
    "0x18bf1a97744539a348304e9d266aac7d446a1582": "Princeton BCC",
    "0x978982772b8e4055b921bf9295c0d74eb36bc54e": "sushiswap"
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

app = Dash(__name__, external_stylesheets=['style.css'])
server = app.server

# Create a list of unique proposals from the 'nodes' list
proposals  = list(unique_titles)
voterz  = list(unique_voters)


# Define the layout of the web application
app.layout = html.Div([
    dcc.Checklist(
        id='choice-filter',
        options=[
            {'label': 'For', 'value': 1},
            {'label': 'Against', 'value': 2},
            {'label': 'Abstain', 'value': 3}
        ],
        value=[1, 2, 3],
    ),
    dcc.Dropdown(
        id='voter-filter',
        options=[{'label': voter, 'value': voter} for voter in voterz],
        multi=True
    ),
    dcc.Dropdown(
        id='proposal-filter',
        options=[{'label': proposal, 'value': proposal} for proposal in proposals],
        multi=True, 
    ),
    html.Div(
        html.A(
            "@kwiz4g",
            
            href="https://twitter.com/kwiz4g",
            target="_blank"
        ), id='twitter-link'
    ),
    dcc.Graph(
        id='sankey',
        figure=sankey_fig,
        config={
            'modeBarButtonsToRemove': ['lasso', 'select']
        }
    )
]) 

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

    filtered_fig.update_layout(
        margin=dict(l=3, r=3, t=30, b=3),
        autosize=True,
        clickmode='none',
        dragmode=False,
        showlegend=False
 #       paper_bgcolor='rgba(0,0,0,0)',
 #       plot_bgcolor='rgba(0,0,0,0)'
    )

    return filtered_fig

if __name__ == '__main__':
    app.run()

