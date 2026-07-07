# iidx-data-tools

Contains some python modules I use for generating [everybodyeverybody.github.io](https://everybodyeverybody.github.io)

- `ac_inf_diff` - Generates the list of songs in the current arcade version of IIDX that are not playable in infinias.
- `song_pack_breakdown` - Generates a cost and song/difficulty breakdown for all available IIDX infinitas song packs.
- `download_textage_tables` - Download and transform song data from [textage.cc](https://textage.cc/) 's javascript modules. Both other modules are dependent on this one.
- `generate_github_pages` - Generates the html and dirs for [everybodyeverybody.github.io](https://everybodyeverybody.github.io)

## Usage

```
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requrements.txt

python3 -m iidx_data_tools.<module name>
```
