---
title: Hardening Tiny Tapeout Projects Locally :: Quicker, easier and cheaper to make your own chip!
source: https://tinytapeout.com/guides/local-hardening/
snapshot: 2026-07-10
---

[Tiny Tapeout](/) > [Guides](/guides/) > Hardening Tiny Tapeout Projects Locally

# Hardening Tiny Tapeout Projects Locally

This document explains how to harden your Tiny Tapeout projects locally, to speed up iteration times. The whole process should take roughly 10 minutes.

It uses the [factory-test](https://github.com/TinyTapeout/ttsky25b-factory-test) project as an example.

## 1. Environment Setup

You need Python 3.11 or newer installed on your system. You can test which python version you have by running `python3 --version`.

On some systems the python binary is called `python` and not `python3`.

If you have an older python version, you can [install uv](https://docs.astral.sh/uv/getting-started/installation/) as an alternative.

You also need a recent version of Docker installed on your system.

We assume your project was cloned to `~/factory-test`. If you don’t have a project yet, and want to follow these instructions to prepare your local setup, you can clone the `factory-test` repo by running the following command:

```
git clone https://github.com/TinyTapeout/ttsky25b-factory-test ~/factory-test
```

## 2. Clone tt-support-tools

Clone the [tt-support-tools](https://github.com/TinyTapeout/tt-support-tools) repo (`main` branch) inside the `tt` directory of your project:

```
cd ~/factory-test
git clone https://github.com/TinyTapeout/tt-support-tools tt
```

## 3. Python and Pip Dependencies

Create a dedicated directory for the virtual Python environment and initialize it. You can use Python’s own `venv`
package or [uv](https://docs.astral.sh/uv/).

venv
uv

```
mkdir ~/ttsetup
python3 -m venv ~/ttsetup/venv
source ~/ttsetup/venv/bin/activate
```

```
mkdir ~/ttsetup
uv venv --python 3.12 ~/ttsetup/venv
source ~/ttsetup/venv/bin/activate
```

**MacOS users:** You may need to install additional dependencies before you can run the next command. Run the following:
`brew install libpng qhull cairo`

Then install the dependencies:

```
pip install -r ~/factory-test/tt/requirements.txt
```

## 4. Set up environment variables

Set up `PDK_ROOT` to the path of the directory that will contain the PDK. `PDK` and `LIBRELANE_TAG` specify, respecively,
the version of the PDK and the version of [LibreLane](https://librelane.readthedocs.io/en/latest/) you will use. Select
the relevant PDK below.

SKY130
GF180MCU
IHP

This is for the SkyWater 130nm PDK.

```
export PDK_ROOT=~/ttsetup/pdk
export PDK=sky130A
export LIBRELANE_TAG=3.0.3
```

This is for the GlobalFoundries 180nm PDK.

```
export PDK_ROOT=~/ttsetup/pdk
export PDK=gf180mcuD
export LIBRELANE_TAG=3.0.3
```

These are for IHP projects using IHP PDKs.

```
export PDK_ROOT=~/ttsetup/pdk
export PDK=ihp-sg13g2
export LIBRELANE_TAG=3.0.3
```

The values of these values may change in the future - you can consult the [tt-gds-action](https://github.com/TinyTapeout/tt-gds-action/blob/main/action.yml)
yaml for the latest values (look at the “default” value for the input called “librelane-version”).

## 5. Install LibreLane

```
pip install librelane==$LIBRELANE_TAG
```

## 6. Harden your project

Congratulations, you are ready to harden your project!

For IHP projects, you need to add the `--ihp` flag to all the `tt_tool.py` commands below, and for GF180MCU projects,
you need to add the `--gf` flag.

First, generate the LibreLane configuration file:

```
cd ~/factory-test
./tt/tt_tool.py --create-user-config
```

Then run the following command to harden the project locally.
Notice that this command **requires you to have Docker** (or a compatible container engine) installed and running.

```
./tt/tt_tool.py --harden
```

It’s also recommended to run the following command, checking for any synthesis / clock warnings:

```
./tt/tt_tool.py --print-warnings
```

# Rehardening

Once you set your environment, you can reharden at any time. Before running `tt_tool.py`, make sure to set the environment variables (as explained in step 1 above), and reactivate the Python virtual environment by running the following command:

```
source ~/ttsetup/venv/bin/activate
```

If you make changes to your project configuration (e.g. increase the number of tiles), you’ll need to update the LibreLane configuration file by running the following command in your project’s directory:

```
./tt/tt_tool.py --create-user-config
```

To reharden, run:

```
./tt/tt_tool.py --harden
```

## Running the RTL tests

```
cd test
pip install -r requirements.txt
make -B
```

## Running the gate level tests

Make sure you select the relevant tab below for the PDK you’re using - IHP models don’t have power pins and therefore
use the unpowered netlist (`nl`) instead of the powered one (`pnl`).

SKY/GF
IHP

```
cd test
pip install -r requirements.txt
TOP_MODULE=$(cd .. && ./tt/tt_tool.py --print-top-module)
cp ../runs/wokwi/final/pnl/$TOP_MODULE.pnl.v gate_level_netlist.v
make -B GATES=yes
```

```
cd test
pip install -r requirements.txt
TOP_MODULE=$(cd .. && ./tt/tt_tool.py --print-top-module)
cp ../runs/wokwi/final/nl/$TOP_MODULE.nl.v gate_level_netlist.v
make -B GATES=yes
```

If the `make -B GATES=yes` command fails with something like `make[1]: *** No rule to make target '[...]/ttsetup/pdk/sky130A/libs.ref/sky130_fd_sc_hd/verilog/primitives.v', needed by 'sim_build/gl/sim.vvp'. Stop.`
then you just need to run a couple of commands in order to enable the PDK.
  
  
First, run `ciel ls`. It should output a list of installed PDKs and their git hash - copy this hash, or the latest if
you have multiple installed. Finally, run `ciel enable <hash>` - for example, `ciel enable 8afc8346a57fe1ab7934ba5a6056ea8b43078e71`.
You should be able to run the gate level tests now.

## Viewing the design in OpenROAD GUI and KLayout

If the GUI fails to open and you see error messages about `could not connect to display :0`, you need to give docker
access to your windowing system. This can be done by running `xhost +local:docker` in the terminal.

To view the hardened design in the OpenROAD GUI, you can use the following command:

```
./tt/tt_tool.py --open-in-openroad
```

For KLayout, you can use:

```
./tt/tt_tool.py --open-in-klayout
```

## Exporting the hardened design to a PNG file

Make sure you have the `librsvg2-bin` and `pngquant` packages installed:

```
sudo apt install librsvg2-bin pngquant
```

then you can use `tt_tool` to generate a render of the GDS as follows:

```
./tt/tt_tool.py --create-png
```

The resulting optimised PNG file is called `gds_render.png` (but note that other `gds_render*` intermediate files are also left behind).
