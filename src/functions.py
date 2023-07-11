import sys
import scipy.io.wavfile
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime

class Figure_creator():
  def __init__(self, fig_size):
    self.fig_size = fig_size
    self.fig = plt.figure(figsize=(12,9))
    
  def add_subplot(self, data, columns, rows, split_num, color, xlabel, ylabel):
    fig_ax = self.fig.add_subplot(columns, rows, split_num)
    fig_ax.set_xlim(0, len(data)-1)
    fig_ax.set_xlabel(xlabel)
    fig_ax.set_ylabel(ylabel)
    fig_ax.plot(data)
    
  def add_subplot_hist(self, data, columns, rows, split_num, color, xlabel, ylabel, bins):
    fig_ax = self.fig.add_subplot(columns, rows, split_num)
    fig_ax.set_xlim(0, len(data)-1)
    fig_ax.set_xlabel(xlabel)
    fig_ax.set_ylabel(ylabel)
    fig_ax.hist(data, bins=bins)
  
  def show(self):
    plt.show()

class FFTAnalysis():
  def __init__(self, row_data):
    self.row_data = row_data
    self.fft_data = []
    self.fft_data_abs_amp = []
    self.data_quantity = len(self.row_data)
    
  def run(self):
    self.fft_data = np.fft.fft(self.row_data)
    fft_data_abs = np.abs(self.fft_data)
    self.fft_data_abs_amp = fft_data_abs / self.data_quantity * 2
    self.fft_data_abs_amp[0] = self.fft_data_abs_amp[0] / 2
  
  def get_fft_data(self):
    return self.fft_data_abs_amp[:int(self.data_quantity/2)+1]
  
  def clear(self):
    self.fft_data = []
    self.fft_data_abs_amp = []
    self.data_quantity = 0
  
  def set_fft_data(self, row_data):
    self.row_data = row_data
    self.data_quantity = len(self.row_data)


class LevelAnalysis():
  def __init__(self, data, rate):
    self.data = data
    self.rate = rate
    self.analysis_data = []
    self.over_th_time = []
    self.over_th_analysis_data = []
    self.peak2peak_data = []
  
  def road_data(self, start_data_number, end_data_number):
    '''
      読み込むデータの範囲を指定
    '''
    self.analysis_data = self.data[start_data_number:end_data_number, 0]
    print("AnalysisData Quantity: ", len(self.analysis_data))
    print("AnalysisData Range: ", start_data_number, " - ", end_data_number)
  
  def get_row_data(self):
    '''
      読み込んだデータをそのまま返す
    '''
    return self.analysis_data
  
  def level_analysis(self, sign, theshold, method):
    """
      閾値を超えたら、その時間を配列に格納
      第一引数: sign
          minus: -1
          plus : +1
      第二引数: theshold
          閾値
      第三引数: method
          level: 閾値解析
          peak : ピーク解析
    """
    if method == "level":
      for item_time in range(len(self.analysis_data)):
        if self.analysis_data[item_time] > (sign * theshold):
          self.over_th_time.append(item_time)
    elif method == "peak":
      for item_time in range(len(self.analysis_data)-1):
        if self.analysis_data[item_time] > sign * theshold:
          if self.analysis_data[item_time-1] < self.analysis_data[item_time] and self.analysis_data[item_time] > self.analysis_data[item_time+1]:
            self.over_th_time.append(item_time)
    
    self.over_th_analysis_data = self.adjest_analysis_data()
    print("Done ", method, " Analysis")
    self.over_th_time = []
  
  def adjest_analysis_data(self):
    '''
      閾値を超えた時間配列から調べて、閾値を超えない部分は0にする
    '''
    data = []
    for item_time in range(len(self.analysis_data)):
      if item_time in self.over_th_time:
          data.append(self.analysis_data[item_time])
      else:
          data.append(0)
    
    return data
  
  def get_sorted_analysis_data(self):
    '''
      閾値を超えたデータをソートして返す
      ファイル名のメタ情報:Sorted
    '''
    sorted_data = np.sort(self.over_th_analysis_data)
    sorted_data = sorted_data[sorted_data != 0]
    meta_string = "Sorted"
    return meta_string, sorted_data
  
  def get_arrange_analysis_data(self):
    '''
      閾値を超えたデータのみを抽出したデータを返す
      ファイル名のメタ情報:Arranged
    '''
    arrange_data = np.array(self.over_th_analysis_data)
    arrange_data = arrange_data[arrange_data != 0]
    meta_string = "Arranged"
    return meta_string, arrange_data
  
  def get_analysis_data(self):
    '''
      閾値を超えたデータの全てを返す
      ファイル名のメタ情報:Row
    '''
    meta_string = "Row"
    return meta_string, self.over_th_analysis_data
  
  def clear_analysis_data(self):
    '''
      解析で使用したデータをクリアする
    '''
    self.analysis_data = []
    self.over_th_time = []
    self.over_th_analysis_data = []

if __name__ == '__main__':
  '''
    第1パラメータ:解析対象のWavファイル
    第2パラメータ:閾値
  '''

  args = sys.argv
  #wav_filename = './wave_data/230610.WAV' 
  wav_filename = args[1]
  theshold = int(args[2])
  
  start_data_number = 0
  end_data_number = 34816950
  end_data_number = 100000
  
  rate, data = scipy.io.wavfile.read(wav_filename)
  print("Rate: ", rate)
  print("Data Quantity: ", data.shape[0])

  figure = Figure_creator((12,9))
  analysis_methods = LevelAnalysis(data, rate)

  analysis_methods.road_data(start_data_number, end_data_number)
  start_time = datetime.datetime.now()
  print("Start Time: ", start_time)
  analysis_methods.level_analysis(1, theshold, "peak")
  #analysis_methods.peak_analysis_biporal(theshold)
  end_time = datetime.datetime.now()
  print("End Time: ", end_time)
  row_data = analysis_methods.get_row_data()
  #meta_string, analysis_data = analysis_methods.get_analysis_data()
  meta_string, analysis_data = analysis_methods.get_arrange_analysis_data()
  #meta_string, analysis_data = analysis_methods.get_peak_analysis_data()
  #meta_string, analysis_data = analysis_methods.get_sorted_analysis_data()
  analysis_methods.clear_analysis_data()

  file_name = 'Analysis.csv'
  save_uid = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
  save_file_name = save_uid + '_' + meta_string + '_' + file_name
  df = pd.DataFrame(analysis_data)
  #df.to_csv(save_file_name, index=False, header=False)

  # fft_analysis = FFTAnalysis(row_data)
  # fft_analysis.run()
  # fft_result = fft_analysis.get_fft_data()

  fig_column = 3
  fig_row = 1

  figure.add_subplot(row_data, fig_column, fig_row, 1, 'r', 'Data Quantity', 'Amplitude')
  figure.add_subplot(analysis_data, fig_column, fig_row, 2, 'r', 'Data Quantity', 'Amplitude')
  #figure.add_subplot_hist(analysis_data, fig_column, fig_row, 3, 'r', 'Amplitude', 'Counts', 100)

  figure.show()