python main.py -c configs/localization/bmn.yaml --weights=/mnt/Workspace/pretrained/BMN.pdparams
python tools/export_model.py -c applications/TableTennis/configs/bmn_tabletennis.yaml -p output/BMN/BMN_epoch_00040.pdparams -o inference/BMN
python tools/export_model.py -c configs/localization/bmn.yaml -p output/BMN/BMN_epoch_00060.pdparams -o inference/BMN/
python tools/predict.py --input_file /mnt/Data_Disk/data/pingpang/solution2/Features_competition_test_A/npy/ --config configs/localization/bmn.yaml --model_file inference/BMN/BMN.pdmodel --params_file inference/BMN/BMN.pdiparams
python main.py -c configs/localization/bmn.yaml -o resume_epoch=13
