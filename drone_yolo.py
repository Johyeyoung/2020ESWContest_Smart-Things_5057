						if correctMap == None:
								# ...... 4.0 : 왜곡된 사진에서 맵만 추출
								image_crop = detect_yolo.imgProcessing(image)
								image_crop = cv2.resize(image_crop,(150,150))
								# ...... 4.1 : yolo를 이용하여 객체 위치 다시 update
								boxes, confidences, classIDs, idxs = detect_yolo.check_obj_yolo(image_crop)
								if len(idxs) > 0:
										print("객체가 발견됐습니다!")
										(c_x, c_y) = detect_yolo.obj_labeling(boxes, confidences, classIDs, idxs, image)
										print("-> 객체의 위치 : {}, {}".format(c_x,c_y))


										# 사진을 전송하는 부분
										if successFrame == 0:
											cv2.imwrite("test.jpg", cv2.resize(image_crop, (800, 600)))
											drone_client.sendToServer(img_origin, (int(c_x), int(c_y)))
											successFrame = 1

										# 서버의 답변을 확인하는 부분
										data = drone_client.sockWaitAnswer()
										if data != '':
											print("___________서버로부터 답변이 왔습니다.___________")
											if data == 'DRONE_close':
												print("DRONE_close, 객체 찾기 모드를 종료합니다.")
												drone_client.sockClose()
												break
											elif data == "DRONE_again":
												print("DRONE_again, 객체를 다시 추적합니다.")
												successFrame = 0




		fps.update()

		# show the output image
		cv2.imshow("output", cv2.resize(image, (800, 600)))
		if cv2.waitKey(1) & 0xFF == ord("q"):
			break
	except:
		pass



fps.stop()

print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()

# release the file pointers
print("[INFO] cleaning up...")
vs.release()
