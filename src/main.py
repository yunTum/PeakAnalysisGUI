import dearpygui.dearpygui as dpg
import tkinter
import tkinter.filedialog as filedialog
import functions as lm
import numpy as np
import scipy.io.wavfile
import asyncio

class AnalysisGUI:
  def __init__(self):
    self.threshold = 0
    self.file_path = ""
    self.analysis_method = ""
    self.save_data_check = False
    self.end_data_number = 0
    self.data = []
    self.rate = 0
    self.analysis_data = []
    self.bins = 0

  def set_file(self, sender, app_data, user_data):
    self.file_path = dpg.get_value("File Path")
    print(f"File Path: {self.file_path}")
    self.rate, self.data = scipy.io.wavfile.read(self.file_path)
    print("Rate: ", self.rate)
    dpg.set_value("Data Length Text", self.data.shape[0])
    dpg.set_value("Data Length", self.data.shape[0])

  def set_setting(self, sender, app_data, user_data):
    self.end_data_number = dpg.get_value("Data Length")
    print(f"Data Length: {self.end_data_number}")
    self.threshold = int(dpg.get_value("AmplitudeThreshold"))
    print(f"Set Threshold: {self.threshold}")
    self.analysis_method = dpg.get_value("AnalysisMethod")
    print(f"Analysis Method: {self.analysis_method}")
    self.save_data_check = dpg.get_value("SaveDataCheckbox")
    print(f"Save Data Check: {self.save_data_check}")
    asyncio.run(self.analysis())
  
  async def analysis(self):
    dpg.set_value("STATUS", "ANALYSING")
    analysis_methods = lm.LevelAnalysis(self.data, self.rate)
    analysis_methods.road_data(0, self.end_data_number)
    analysis_methods.level_analysis(1, self.threshold, self.analysis_method)
    meta_string, self.analysis_data = analysis_methods.get_arrange_analysis_data()
    analysis_methods.clear_analysis_data()
    dpg.set_value("STATUS", "DONE")
    self.plot()

  # row data plot
  def plot(self):
    if (dpg.does_item_exist("Peak Plot")):
      dpg.delete_item("Peak Plot", children_only=True)
    data_len = self.analysis_data.shape[0]
    print(f"data_len: {data_len}")
    dpg.set_value("Analysis Data Length Text", data_len)
    if (data_len == 0):
      dpg.set_value("STATUS", "DATA LENGTH IS 0")
      return
    dpg.add_plot_legend(parent="Peak Plot")
    dpg.add_plot_axis(dpg.mvXAxis, label="Data Length", no_gridlines=True, tag="x_axis", parent="Peak Plot")
    dpg.set_axis_limits(dpg.last_item(), 0, data_len+10)
    dpg.add_plot_axis(dpg.mvYAxis, label="Amplitude", tag="y_axis", parent="Peak Plot")
    y_max = self.analysis_data.max()
    print(f"y_max: {y_max}")
    dpg.set_value("Height Max Text", y_max)
    dpg.set_axis_limits("y_axis", 0, y_max+100)
    time = np.arange(0, data_len, 1)
    # add series to y axis
    dpg.add_line_series(time, self.analysis_data, parent="y_axis")

  # histogram plot
  def barplot(self, sender, app_data, user_data):
    self.bins = dpg.get_value("Bins")
    if (dpg.does_item_exist("Bar Plot")):
      dpg.delete_item("Bar Plot", children_only=True)
    hist, bins = np.histogram(self.analysis_data, bins=self.bins)
    dpg.add_plot_legend(parent="Bar Plot")
    dpg.add_plot_axis(dpg.mvXAxis, label="Amplitude", no_gridlines=True, tag="bar_x_axis", parent="Bar Plot")
    dpg.set_axis_limits(dpg.last_item(), 0, bins.max()+100)
    dpg.add_plot_axis(dpg.mvYAxis, label="Counts", tag="bar_y_axis", parent="Bar Plot")
    hist_max = hist.max()
    dpg.set_axis_limits("bar_y_axis", 0, hist_max+10)
    bins_width = bins[1] - bins[0]
    # add series to y axis
    dpg.add_bar_series(bins.tolist(), hist.tolist(), weight=bins_width, parent="bar_y_axis")



def open_file(sender, app_data, user_data):
    root = tkinter.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    root.destroy()
    dpg.set_value("File Path", file_path)

if __name__ == '__main__':
  gui = AnalysisGUI()
  dpg.create_context()
  dpg.create_viewport(title='Wave Analysis', width=1100, height=950, resizable=False)
  dpg.setup_dearpygui()
  setting_var_width = 300
  with dpg.window(label="Setting Window", width=setting_var_width, height=920, no_move=True, no_close=True, no_resize=True):
    with dpg.group(horizontal=True):
      dpg.add_input_text(tag="File Path")
      dpg.add_button(label="Select File", callback=open_file)
    dpg.add_button(label="File Load", callback=gui.set_file)

    dpg.add_text(label="0", tag="Data Length Text", default_value=0)
    dpg.add_input_int(label="Data Length", tag="Data Length")
    
    dpg.add_combo(label="MethodCombo", items=["level", "peak"], default_value="peak", tag="AnalysisMethod")
    dpg.add_input_text(label="threshold", tag="AmplitudeThreshold", hint="Amplitude Threshold", decimal=True, default_value=500)
    dpg.add_checkbox(label="SaveDataCheckbox", tag="SaveDataCheckbox")
    dpg.add_spacer(height=5)
    dpg.add_button(label="Analysis", callback=gui.set_setting)
    with dpg.group(horizontal=True):
      dpg.add_text("STATUS: ")
      dpg.add_text(tag="STATUS", default_value="WAIT")
    dpg.add_spacer(height=10)
    dpg.add_text("Results")
    with dpg.group(horizontal=True):
      dpg.add_text("Peak Data Length: ")
      dpg.add_text(label="0", tag="Analysis Data Length Text", default_value=0)
    with dpg.group(horizontal=True):
      dpg.add_text("Height Max: ")
      dpg.add_text(label="0", tag="Height Max Text", default_value=0)
    
    dpg.add_spacer(height=30)
    dpg.add_text("Bar Plot")
    dpg.add_input_int(label="Bins", tag="Bins")
    dpg.add_button(label="Plot", callback=gui.barplot)
    

  with dpg.window(label="Gragh Window", width=805, height=920, pos=[setting_var_width, 0],no_move=True, no_close=True, no_resize=True):
    dpg.add_plot(label="Peak Plot", tag="Peak Plot", height=430, width=700)
    dpg.add_plot(label="Bar Plot", tag="Bar Plot", height=430, width=700)

  dpg.show_viewport()
  dpg.start_dearpygui()
  dpg.destroy_context()