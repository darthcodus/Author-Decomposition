package com.cs544conquistador; /**
 * Created by longpengjiao on 4/11/16.
 */

import edu.stanford.nlp.simple.*;

import java.io.*;

public class AuthorshipDecompUtil {

    String docString;
    Document doc;

    public AuthorshipDecompUtil(File file){
        BufferedReader br = null;
        try {

            String sCurrentLine;

            br = new BufferedReader(new FileReader(file));
            StringBuilder sb = new StringBuilder();
            while ((sCurrentLine = br.readLine()) != null) {
                sb.append(sCurrentLine);
            }

            docString = sb.toString();
            //System.out.println(docString);
            doc = new Document(docString);


        } catch (IOException e) {
            e.printStackTrace();
        } finally {
            try {
                if (br != null)br.close();
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
    }

    public void getSentencesFile(String outPutFileName){

        try {
            if(outPutFileName == null || outPutFileName.length() == 0){
                throw new IllegalArgumentException("output file name can't be null or empty!");
            }
            StringBuilder sb = new StringBuilder();
            for (Sentence sent : doc.sentences()) {
                //System.out.println(sent.toString());
                sb.append(sent.toString()+"\n");
            }

            String content = sb.toString();

            File file = new File(outPutFileName);

            // if file doesnt exists, then create it
            if (!file.exists()) {
                System.out.println("creating new file");
                file.createNewFile();
            }else{
                System.out.println("replacing older file");
            }

            FileWriter fw = new FileWriter(file.getAbsoluteFile());
            BufferedWriter bw = new BufferedWriter(fw);
            bw.write(content);
            bw.close();

            System.out.println("Done");

        } catch (IOException e) {
            e.printStackTrace();
        }

    }

    public static void main(String[] args) {

        String filePath = args[0];

        try {
            //System.out.println(System.getProperty("user.dir"));
            System.out.println("Getting file with path:" + args[0]);
            File file = new File(filePath);

            if (file.createNewFile()){
                System.out.println("input doesn't exist");
            }else{
                System.out.println("Found input file.");
            }

            AuthorshipDecompUtil util = new AuthorshipDecompUtil(file);

            util.getSentencesFile(args[1]);

        } catch (IOException e) {
            e.printStackTrace();
        }

    }
}
