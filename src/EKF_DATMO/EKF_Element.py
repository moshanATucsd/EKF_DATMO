import numpy as np

class EKF_Element :
	def __init__(self, freq=200):
		self.freq = freq
		assert(self.freq != 0)
		self.dt = 1.0/freq 
		#State-transition model
		self.A = np.matrix([
				[1,0,self.dt,0],
				[0,1,0,self.dt],
				[0,0,1,0],
				[0,0,0,1]
		]) 
		#Observation model
		self.H = np.matrix([[1,0,0,0],[0,1,0,0]]) 

		#Process/State noise
		vel_noise_std = 1e-3
		pos_noise_std = 1e-3
		self.Q = np.matrix([
				[pos_noise_std*pos_noise_std,0,0,0],
				[0,pos_noise_std*pos_noise_std,0,0],
				[0,0,vel_noise_std*vel_noise_std,0],
				[0,0,0,vel_noise_std*vel_noise_std]
		]) 

		#Sensor/Measurement noise
		measurement_noise_std = 1e0
		self.R = measurement_noise_std * measurement_noise_std * np.identity(2) 

		self.x = np.zeros((4,1)) #Initial state vector [x,y,vx,vy]
		self.sigma = np.identity(4) #Initial covariance matrix
		
	
	def getState(self) :
		return self.x
		
	def getCovariance(self) :
		return self.sigma
		
		
	def predictState(self, A, x):
		'''
		:param A: State-transition model matrix
		:param x: Current state vector
		:return x_p: Predicted state vector as numpy array
		'''
		x_p = np.dot(A,x)
		return x_p

	def predictCovariance(self, A, sigma, Q):
		sigma_p = np.dot( np.dot(A, sigma), np.transpose(A)) + Q
		return sigma_p

	def calculateKalmanGain(self, sigma_p, H, R):
		a = np.dot(sigma_p, np.transpose(H))
		b = np.linalg.inv(np.dot(H, np.dot(sigma_p, np.transpose(H)))+R)
		k = np.dot( a, b)
		return k

	def correctState(self, z, x_p, k, H):
		'''
		:param z: Measurement vector
		:param x_p: Predicted state vector
		:param k: Kalman gain
		:param H: Observation model
		:return x: Corrected state vector as 4x1 numpy array
		'''
		a = np.dot(k,(z - np.dot(H,x_p)))
		x= x_p + a
		return x

	def correctCovariance(self, sigma_p, k, H):
		sigma = np.dot((np.identity(self.x.shape[0])-np.dot(k, H)), sigma_p)
		return sigma

	def state_callback(self):
		self.x = self.predictState(self.A, self.x)
		self.sigma = self.predictCovariance(self.A, self.sigma, self.Q)

	def measurement_callback(self, measurement):
		'''
		:param measurement: vector of measured coordinates
		'''
		k = self.calculateKalmanGain(self.sigma, self.H, self.R)
		self.x = self.correctState(measurement, self.x, k, self.H)
		self.sigma = self.correctCovariance(self.sigma, k, self.H)
	
	
