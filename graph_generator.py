import json
import os
from matplotlib import pyplot as plt
import pyshark
from tqdm import tqdm

PCAPS_FOLDER = "pcaps"
GRAPH_FOLDER = "graphs"


def fill_zeros(timeline):
    """
    Fill zeros in a timeline list with the maximum value encountered so far.
    """
    max_val = 0
    for ind, val in enumerate(timeline):
        if val == 0:
            timeline[ind] = max_val
        else:
            max_val = val
    return timeline


def extract_timelines(pcap):
    """
    Extract handshakes, servers, and resumptions timelines for a given pcap file.
    """
    num_handshakes = 0
    num_servers = 0
    num_resumptions = 0

    handshake_timeline = [0] * 300
    server_timeline = [0] * 300
    resumption_timeline = [0] * 300

    capture_times = pyshark.FileCapture(f"{PCAPS_FOLDER}/{pcap}")
    zero_time = float(capture_times[0].sniff_timestamp)

    capture = pyshark.FileCapture(f"{PCAPS_FOLDER}/{pcap}", display_filter='tls.handshake.type == 1')

    servers = []
    for c in capture:
        rec_time = float(c.sniff_timestamp) - zero_time
        if rec_time > 300:
            break

        num_handshakes += 1
        handshake_timeline[int(rec_time)] = num_handshakes

        try:
            if hasattr(c['tls'], "handshake_extensions_server_name"):
                server_name = c['tls'].handshake_extensions_server_name
                if server_name in servers:
                    num_servers += 1
                    server_timeline[int(rec_time)] = num_servers
                else:
                    servers.append(server_name)
        except KeyError:
            pass

    capture.close()

    capture = pyshark.FileCapture(f"{PCAPS_FOLDER}/{pcap}", display_filter='tls.handshake.type == 2 && (tls.handshake.extension.type == 41 || tls.resumed)')
    for c in capture:
        rec_time = float(c.sniff_timestamp) - zero_time
        if rec_time > 300:
            break

        num_resumptions += 1
        resumption_timeline[int(rec_time)] = num_resumptions

    capture.close()

    handshake_timeline = fill_zeros(handshake_timeline)
    server_timeline = fill_zeros(server_timeline)
    resumption_timeline = fill_zeros(resumption_timeline)

    return handshake_timeline, server_timeline, resumption_timeline


def get_timelines():
    """
    Extract handshake, server, and resumption timelines for all pcaps.
    """
    handshake_timelines = {}
    server_timelines = {}
    resumption_timelines = {}

    for pcap in tqdm(pcaps):
        if not pcap.endswith(".pcap"):
            continue

        handshake_timeline, server_timeline, resumption_timeline = extract_timelines(pcap)

        handshake_timelines[pcap] = handshake_timeline
        server_timelines[pcap] = server_timeline
        resumption_timelines[pcap] = resumption_timeline

    return handshake_timelines, resumption_timelines, server_timelines


def load_or_generate_timelines():
    """
    Load existing timeline data from JSON files or generate new timelines and save them to JSON.
    """
    files = os.listdir()
    tls_files = ["client_hello.json", "resumptions.json", "servers.json"]

    if all(element in files for element in tls_files):
        with open("client_hello.json") as f:
            stats_handshakes = json.load(f)

        with open("resumptions.json") as f:
            stats_resumptions = json.load(f)

        with open("servers.json") as f:
            stats_servers = json.load(f)
    else:
        stats_handshakes, stats_resumptions, stats_servers = get_timelines()

        with open(f"client_hello.json", "w") as f:
            json.dump(stats_handshakes, f)

        with open(f"resumptions.json", "w") as f:
            json.dump(stats_resumptions, f)

        with open(f"servers.json", "w") as f:
            json.dump(stats_servers, f)

    return stats_handshakes, stats_resumptions, stats_servers


def plot_graphs(stats_handshakes, stats_resumptions, stats_servers):
    """
    Plot the graphs for each application using the extracted or loaded timelines.
    """
    for app in stats_handshakes:
        plt.rcParams.update({'font.size': 16})
        fig, ax = plt.subplots()
        x = range(len(stats_handshakes[app]) + 1)
        y = [0] + stats_handshakes[app]
        y2 = [0] + stats_resumptions[app]
        y3 = [0] + stats_servers[app]

        ax.plot(x, y, label="Client Hellos")
        ax.plot(x, y2, label="Resumptions")
        ax.plot(x, y3, label="Same Servers")

        ax.set_xlabel("Seconds")
        ax.set_ylabel("Count")
        ax.legend(fancybox=True, framealpha=0.5)
        app_name = app.replace(".pcap", "")
        ax.set_title(app_name)

        plt.savefig(f"graphs/{app_name}.pdf", bbox_inches="tight")
        plt.close(fig)  


def main():
    global pcaps
    pcaps = os.listdir(PCAPS_FOLDER)

    stats_handshakes, stats_resumptions, stats_servers = load_or_generate_timelines()
    plot_graphs(stats_handshakes, stats_resumptions, stats_servers)


if __name__ == "__main__":
    main()
