import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# Frequency bands we want to evaluate
# ---------------------------------------------------------
FREQ_BANDS = [125, 250, 500, 1000, 2000, 4000]

# ---------------------------------------------------------
# Absorption data for each material/raft, per frequency band.
# ---------------------------------------------------------
MATERIALS_DATA = {
    "Select Material": {
        125: 0.00, 250: 0.00, 500: 0.00,
        1000: 0.00, 2000: 0.00, 4000: 0.00
    },
    "Plasterboard on Frame 50mm": {
        125: 0.15, 250: 0.10, 500: 0.06,
        1000: 0.04, 2000: 0.04, 4000: 0.05
    },
    "Smooth Unpainted Concrete": {
        125: 0.01, 250: 0.01, 500: 0.02,
        1000: 0.02, 2000: 0.02, 4000: 0.05
    },
    "5mm Needlefelt Carpet": {
        125: 0.01, 250: 0.02, 500: 0.05,
        1000: 0.15, 2000: 0.30, 4000: 0.40
    },
    "Linoleum or vinyl on Concrete": {
        125: 0.02, 250: 0.02, 500: 0.03,
        1000: 0.04, 2000: 0.04, 4000: 0.05
    },
    "4mm Glass": {
        125: 0.30, 250: 0.20, 500: 0.10,
        1000: 0.07, 2000: 0.05, 4000: 0.02
    },
    "Class A": {
        125: 0.50, 250: 0.70, 500: 0.90,
        1000: 0.90, 2000: 0.90, 4000: 0.90
    },
    "Class B": {
        125: 0.40, 250: 0.60, 500: 0.80,
        1000: 0.80, 2000: 0.80, 4000: 0.70
    },
    "Class C": {
        125: 0.20, 250: 0.40, 500: 0.60,
        1000: 0.60, 2000: 0.60, 4000: 0.50
    },
    "Class D": {
        125: 0.10, 250: 0.10, 500: 0.30,
        1000: 0.30, 2000: 0.30, 4000: 0.20
    },
    "Class E": {
        125: 0.05, 250: 0.05, 500: 0.15,
        1000: 0.15, 2000: 0.15, 4000: 0.10
    },
    "Egg cartons directly on wall ": {
        125: 0.01, 250: 0.07, 500: 0.43,
        1000: 0.62, 2000: 0.51, 4000: 0.70
    },
    # Example raft with total sabins per raft
    "Ecophon Solo at 1000mm ODS": {
        125: 1.10, 250: 1.20, 500: 3.70,
        1000: 5.50, 2000: 5.60, 4000: 5.30
    }
}

def main():
    st.title("Frequency-Dependent Reverb Estimator")

    st.write(
        "This tool calculates the reverberation time (T60) across octave bands using Sabine's formula.\n"
        "It also allows specifying multiple materials for ceiling, walls, floor, and optionally an acoustic raft."
    )

    # Keep a list of dictionaries in session state so it persists
    if "results" not in st.session_state:
        st.session_state["results"] = []

    # ---------------------------------------------------------
    # ROOM GEOMETRY INPUTS
    # ---------------------------------------------------------
    st.subheader("Room Geometry")
    length = st.number_input("Room Length (m)", value=5.0, min_value=0.0, step=0.1)
    width = st.number_input("Room Width (m)", value=4.0, min_value=0.0, step=0.1)
    room_height = st.number_input("Room Height (m)", value=3.0, min_value=0.0, step=0.1)

    # ---------------------------------------------------------
    # CEILING
    # ---------------------------------------------------------
    st.subheader("Ceiling")
    ceiling_cols = st.columns(3)
    ceiling_main_mat = ceiling_cols[0].selectbox("Ceiling Main Material", list(MATERIALS_DATA.keys()))
    ceiling_add_mat  = ceiling_cols[1].selectbox("Ceiling Add. Material", list(MATERIALS_DATA.keys()))
    ceiling_add_area = ceiling_cols[2].number_input("Ceiling Add. Area (m²)", value=0.0, min_value=0.0, step=0.1)

    # ---------------------------------------------------------
    # WALLS
    # ---------------------------------------------------------
    st.subheader("Walls")
    walls_cols = st.columns(3)
    walls_main_mat = walls_cols[0].selectbox("Walls Main Material", list(MATERIALS_DATA.keys()))
    walls_add_mat  = walls_cols[1].selectbox("Walls Add. Material", list(MATERIALS_DATA.keys()))
    walls_add_area = walls_cols[2].number_input("Walls Add. Area (m²)", value=0.0, min_value=0.0, step=0.1)

    # ---------------------------------------------------------
    # FLOOR
    # ---------------------------------------------------------
    st.subheader("Floor")
    floor_cols = st.columns(3)
    floor_main_mat = floor_cols[0].selectbox("Floor Main Material", list(MATERIALS_DATA.keys()))
    floor_add_mat  = floor_cols[1].selectbox("Floor Add. Material", list(MATERIALS_DATA.keys()))
    floor_add_area = floor_cols[2].number_input("Floor Add. Area (m²)", value=0.0, min_value=0.0, step=0.1)

    # ---------------------------------------------------------
    # ACOUSTIC HANGING RAFTS
    # ---------------------------------------------------------
    st.subheader("Acoustic Rafts")
    raft_cols = st.columns(2)
    raft_mat = raft_cols[0].selectbox("Raft Material", list(MATERIALS_DATA.keys()))
    raft_count = raft_cols[1].number_input("Number of Rafts", value=0, min_value=0, step=1)

    # ---------------------------------------------------------
    # Calculate Button
    # ---------------------------------------------------------
    if st.button("Calculate Multi-Band RT"):
        # Calculate geometry
        volume = length * width * room_height
        floor_area = length * width
        wall_area = 2.0 * (length + width) * room_height
        ceiling_area = floor_area

        data_dict = {
            "Room_Length_m": length,
            "Room_Width_m": width,
            "Room_Height_m": room_height,
            "Ceiling_Main_Material": ceiling_main_mat,
            "Ceiling_Add_Material": ceiling_add_mat,
            "Ceiling_Add_Area_m2": ceiling_add_area,
            "Walls_Main_Material": walls_main_mat,
            "Walls_Add_Material": walls_add_mat,
            "Walls_Add_Area_m2": walls_add_area,
            "Floor_Main_Material": floor_main_mat,
            "Floor_Add_Material": floor_add_mat,
            "Floor_Add_Area_m2": floor_add_area,
            "Raft_Material": raft_mat,
            "Number_of_Rafts": raft_count,
        }

        t60_values = {}
        result_lines = []

        for freq in FREQ_BANDS:
            alpha_ceiling_main = MATERIALS_DATA.get(ceiling_main_mat, {}).get(freq, 0.0)
            alpha_ceiling_add  = MATERIALS_DATA.get(ceiling_add_mat, {}).get(freq, 0.0)

            alpha_walls_main   = MATERIALS_DATA.get(walls_main_mat, {}).get(freq, 0.0)
            alpha_walls_add    = MATERIALS_DATA.get(walls_add_mat, {}).get(freq, 0.0)

            alpha_floor_main   = MATERIALS_DATA.get(floor_main_mat, {}).get(freq, 0.0)
            alpha_floor_add    = MATERIALS_DATA.get(floor_add_mat, {}).get(freq, 0.0)

            # Adjust area if additional coverage is bigger than the total
            effective_ceiling_main_area = max(0.0, ceiling_area - ceiling_add_area)
            effective_walls_main_area   = max(0.0, wall_area - walls_add_area)
            effective_floor_main_area   = max(0.0, floor_area - floor_add_area)

            A_ceiling_main = effective_ceiling_main_area * alpha_ceiling_main
            A_ceiling_add  = ceiling_add_area * alpha_ceiling_add
            A_walls_main   = effective_walls_main_area   * alpha_walls_main
            A_walls_add    = walls_add_area   * alpha_walls_add
            A_floor_main   = effective_floor_main_area   * alpha_floor_main
            A_floor_add    = floor_add_area   * alpha_floor_add

            total_absorption = (
                A_ceiling_main + A_ceiling_add +
                A_walls_main   + A_walls_add   +
                A_floor_main   + A_floor_add
            )

            # Raft absorption (sabins per raft * count)
            alpha_raft = MATERIALS_DATA.get(raft_mat, {}).get(freq, 0.0)
            A_rafts = raft_count * alpha_raft
            total_absorption += A_rafts

            # Sabine T60
            t60 = 0.0
            if total_absorption > 0:
                t60 = 0.161 * (volume / total_absorption)

            t60_values[freq] = t60
            data_dict[f"T60_{freq}Hz"] = round(t60, 3)
            result_lines.append(f"- **{freq} Hz**: {t60:.2f} s")

        # TMF (average T60 for frequencies 500-2000 Hz)
        freq_500_2000 = [val for f, val in t60_values.items() if 500 <= f <= 2000]
        tmf = sum(freq_500_2000) / len(freq_500_2000) if freq_500_2000 else 0.0
        data_dict["TMF"] = round(tmf, 3)
        result_lines.append(f"- **TMF (500-2000 Hz)**: {tmf:.2f} s")

        # Display results
        st.markdown("### Estimated T60 (seconds):")
        for line in result_lines:
            st.markdown(line)

        # Append to session state
        st.session_state["results"].append(data_dict)

        # -- Plot the T60 for the current calculation --
        freqs = list(t60_values.keys())
        t60vals = [t60_values[f] for f in freqs]

        fig, ax = plt.subplots()
        ax.bar(freqs, t60vals)
        ax.set_xlabel("Frequency (Hz)")
        ax.set_ylabel("T60 (s)")
        ax.set_title("Reverberation Time per Frequency Band")
        st.pyplot(fig)

        st.success("Calculation complete! See 'Cumulative Results' section below.")

    # ---------------------------------------------------------
    # Show a cumulative table of results
    # ---------------------------------------------------------
    st.subheader("Cumulative Results")

    if st.session_state["results"]:
        df = pd.DataFrame(st.session_state["results"])
        st.dataframe(df)

        # Convert the entire DataFrame to CSV
        csv_text = df.to_csv(index=False)
        # Escape newlines and quotes for safe injection into JavaScript
        escaped_csv = csv_text.replace("\n", "\\n").replace("\"", "\\\"")

        # Create a button that uses a small JS snippet to write to clipboard
        copy_button = f"""
            <button onclick="navigator.clipboard.writeText(`{escaped_csv}`); 
                     alert('Copied results to clipboard!')">
                Copy CSV to Clipboard
            </button>
        """
        st.markdown(copy_button, unsafe_allow_html=True)

    else:
        st.info("No results yet. Complete a calculation to see cumulative results here.")

if __name__ == "__main__":
    main()
