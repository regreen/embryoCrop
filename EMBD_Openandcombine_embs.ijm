function sort_embs(embs){
	nFolders=0;
	for (i=0; i<embs.length; i++){
		if (startsWith(embs[i],"Emb") || startsWith(embs[i],"xEmb")) nFolders=nFolders+1;
	}
	numbs = newArray(nFolders);
	res = newArray(nFolders);
	ind=0;
	for (i=0; i<embs.length; i++){
		print(embs[i]);
		if (startsWith(embs[i],"Emb")){
			//print(substring(embs[i],3,lengthOf(embs[i])-1));
			numbs[ind]=parseInt(substring(embs[i],3,lengthOf(embs[i])-1));
			ind++;
		} else if (startsWith(embs[i],"xEmb")) {
			//print(substring(embs[i],4,lengthOf(embs[i])-1));
			numbs[ind]=1000+parseInt(substring(embs[i],4,lengthOf(embs[i])-1));
			ind++;
		}
	}
	Array.sort(numbs);
	for (i=0; i<numbs.length; i++){
		if (numbs[i]<1000) res[i]="Emb"+numbs[i]+"/";
		else res[i]="xEmb"+(numbs[i]-1000)+"/";
	}
	return res;
}
RNAL = newArray("EMBD1608/");
//RNAL = newArray("EMBD1209/","EMBD1206/","EMBD1210/","EMBD1207/","EMBD1211/","EMBD1208/");

date = newArray("20171130T122304");
folder = "Z:/cropped/";
folderOut2 = "Z:/EMBD_fiji_processed/";
fSize = 24;
setFont( "SansSerif", fSize);
for (r=0; r<date.length; r++){
for (l=0; l<RNAL.length; l++){
	RNA = RNAL[l];
	listStrains = getFileList(folder+RNA);
	for (j = 0; j < listStrains.length; j++){	
		if (listStrains[j] == "GLS/"){
		//false && (put before list strains to skip GLS and only run MS) 
		if (RNA!="EMBD0000/") embPath=folder+RNA+"GLS/";
			else embPath=folder+RNA+"GLS/"+date[r]+"/";
			listGLS = getFileList(embPath);
			listGLS = sort_embs(listGLS);
			k=0;
			for (i = 0; i < listGLS.length; i++){
				name = listGLS[listGLS.length-i-1];
				listFile = getFileList(embPath+name);
				if (!endsWith(listFile[0], "tif")) listFile[0]=listFile[1];
				if (substring(listFile[0], lengthOf(listFile[0])-36, lengthOf(listFile[0])-21)==date[r]){
					print(substring(name, 0, lengthOf(name)-1));
					run("Image Sequence...", "open="+embPath+name+listFile[0]+" sort");
					rename("tmp");
					t = nSlices/18/3;
					run("Stack to Hyperstack...", "order=xyczt(default) channels=3 slices=18 frames="+t+" display=Color");
					run("Channels Tool...");
					run("Green");
					Stack.setChannel(2);
					run("Red");
					Stack.setChannel(3);
					run("Grays");
					selectWindow("Channels");
					run("Close");
					run("Duplicate...", "title=tmp-rgb duplicate channels=1-2 slices=1-18 frames=1-31");
					selectWindow("tmp");
					run("Duplicate...", "title=tmp-gray duplicate channels=3 slices=1-18 frames=1-31");
					selectWindow("tmp-rgb");
					run("Make Composite");
					selectWindow("tmp-rgb");
					run("RGB Color", "slices frames");
					selectWindow("tmp-rgb");
					run("Z Project...", "projection=[Max Intensity] all");
					selectWindow("tmp-gray");
					run("RGB Color", "slices frames");
					run("Duplicate...", "title=tmp-grayC duplicate slices=9 frames=1-31");
					selectWindow("tmp-gray");
					close();
					selectWindow("tmp-rgb");
					close();
					selectWindow("tmp");
					close();
					run("Combine...", "stack1=tmp-grayC stack2=MAX_tmp-rgb");
					rename("tmp");
					for (n=1; n<nSlices+1; n++){
						setSlice(n);
						drawString(substring(name,0,lengthOf(name)-1)+" "+substring(listFile[0], lengthOf(listFile[0])-20,lengthOf(listFile[0])-15), 10, 5+fSize);
					}
					if (k>0) run("Combine...", "stack1=tmp stack2="+substring(RNA,0,lengthOf(RNA)-1)+"_"+"GLS"+"_"+date[r]+" combine");
					rename(substring(RNA,0,lengthOf(RNA)-1)+"_"+"GLS"+"_"+date[r]);
					k++;
				}
			}
			/*if (k>0) {
				if (RNA!="EMBD0626/") {
					if (!File.exists(folderOut2)) File.makeDirectory(folderOut2);
					saveAs("Tiff", folderOut2+substring(RNA,0,lengthOf(RNA)-1)+"_"+"GLS"+"_"+date[r]+".tif");
				}
				else {
					if (!File.exists(folderOut2+"EMBD0000/")) File.makeDirectory(folderOut2+"EMBD0000/");
					saveAs("Tiff", folderOut2+"EMBD0000/"+substring(RNA,0,lengthOf(RNA)-1)+"_"+"GLS"+"_"+date[r]+".tif");	
				}
//				close();
			}
		}
		if (listStrains[j] == "MS/"){
			if (RNA!="EMBD0000/") embPath=folder+RNA+"MS/";
			else embPath=folder+RNA+"MS/"+date[r]+"/";
			listMS = getFileList(embPath);
			listMS = sort_embs(listMS);
			k=0;
			for (i = 0; i < listMS.length; i++){
				name = listMS[listMS.length-i-1];
				print(embPath+name);
				listFile = getFileList(embPath+name);
				if (substring(listFile[0], lengthOf(listFile[0])-36, lengthOf(listFile[0])-21)==date[r]){
					print(substring(name, 0, lengthOf(name)-1));
					run("Image Sequence...", "open="+embPath+name+listFile[0]+" sort");
					rename("tmp");
					t = nSlices/18/3;
					run("Stack to Hyperstack...", "order=xyczt(default) channels=3 slices=18 frames="+t+" display=Color");
					run("Channels Tool...");
					run("Green");
					setMinAndMax(0, 12225);
					Stack.setChannel(2);
					run("Red");
					setMinAndMax(0, 19025);
					Stack.setChannel(3);
					run("Grays");
					selectWindow("Channels");
					run("Close");
					run("Duplicate...", "title=tmp-rgb duplicate channels=1-2 slices=1-18 frames=1-31");
					selectWindow("tmp");
					run("Duplicate...", "title=tmp-gray duplicate channels=3 slices=1-18 frames=1-31");
					selectWindow("tmp-rgb");
					run("Make Composite");
					selectWindow("tmp-rgb");
					run("RGB Color", "slices frames");
					selectWindow("tmp-rgb");
					run("Z Project...", "projection=[Max Intensity] all");
					selectWindow("tmp-gray");
					run("RGB Color", "slices frames");
					run("Duplicate...", "title=tmp-grayC duplicate slices=9 frames=1-31");
					selectWindow("tmp-gray");
					close();
					selectWindow("tmp-rgb");
					close();
					selectWindow("tmp");
					close();
					run("Combine...", "stack1=tmp-grayC stack2=MAX_tmp-rgb");
					rename("tmp");
					for (n=1; n<nSlices+1; n++){
						setSlice(n);
						drawString(substring(name,0,lengthOf(name)-1)+" "+substring(listFile[0], lengthOf(listFile[0])-20,lengthOf(listFile[0])-15), 10, 5+fSize);
					}
					if (k>0) run("Combine...", "stack1=tmp stack2="+substring(RNA,0,lengthOf(RNA)-1)+"_"+"MS"+"_"+date[r]+" combine");
					rename(substring(RNA,0,lengthOf(RNA)-1)+"_"+"MS"+"_"+date[r]);
					k++;
				}
			}
			if (k>0) {
				if (RNA!="EMBD0000/") {
					if (!File.exists(folderOut2)) File.makeDirectory(folderOut2);
					saveAs("Tiff", folderOut2+substring(RNA,0,lengthOf(RNA)-1)+"_"+"MS"+"_"+date[r]+".tif");
				}
				else {
					if (!File.exists(folderOut2+"EMBD0000/")) File.makeDirectory(folderOut2+"EMBD0000/");
					saveAs("Tiff", folderOut2+"EMBD0000/"+substring(RNA,0,lengthOf(RNA)-1)+"_"+"MS"+"_"+date[r]+".tif");
				}
//				close();
			}
		}*/
	}
}
}