Java utility to split sentences in txt document
=============================================

First make sure you're using java 1.8 (the version of stanford corenlp I'm using needs java 1.8)

Use maven to package executable jar:

```
mvn package
```

The previous will create: 
target/sentenceSplitUtil-jar-with-dependencies.jar

Run program with:

```
java -jar sentenceSplitUtil-jar-with-dependencies.jar <inputfile path> <outputfile path>
```


