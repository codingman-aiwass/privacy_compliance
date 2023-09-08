package android;
import java.io.File;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.Set;
import java.util.HashSet;
import java.util.List;
import java.util.ArrayList;
import java.nio.file.Files;
import java.nio.file.Paths;

import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.CoreDocument;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
public class ProcessStr {
    private static final Pattern HUMP_PATTERN = Pattern.compile("([a-z\\d])([A-Z])");
    private static final Set<String> STOP_WORDS = new HashSet<>();

    static {
        try {
            List<String> stopWordsList = Files.readAllLines(
                    Paths.get(System.getProperty("user.home"), "nltk_data" + File.separator + "corpora" + File.separator + "stopwords" + File.separator + "english"));
            for (String stopWord : stopWordsList) {
                STOP_WORDS.add(stopWord.toLowerCase());
            }
        } catch (Exception e) {
            // Handle exception
        }
    }
    private static final StanfordCoreNLP PIPELINE = new StanfordCoreNLP();

    public static String preProcessingSingle(String rawDoc) {
        List<String> updatedList = new ArrayList<>();

        String characterList = rawDoc.replaceAll("[^a-zA-Z]+", " ");

        for (String token : characterList.split(" ")) {
            token = humpToUnderline(token);
            if (token.contains("_")) {
                for (String item : token.split("_")) {
                    if (item.length() > 1) {
                        updatedList.add(item);
                    }
                }
            } else if (token.length() > 1) {
                updatedList.add(token);
            }
        }

        List<String> tokensLemmaed = new ArrayList<>(updatedList.size());
        for (String word : updatedList) {
            if (STOP_WORDS.contains(word)) {
                tokensLemmaed.add(word);
                continue;
            }
            CoreDocument document = new CoreDocument(word);
            PIPELINE.annotate(document);
            CoreLabel label = document.tokens().get(0);
            tokensLemmaed.add(label.lemma());
        }

        StringBuilder resultBuilder = new StringBuilder();
        for (String lemma : tokensLemmaed) {
            resultBuilder.append(lemma).append(" ");
        }
        return resultBuilder.toString().trim();
    }

    private static String humpToUnderline(String humpStr) {
        Matcher matcher = HUMP_PATTERN.matcher(humpStr);
        return matcher.replaceAll("$1_$2").toLowerCase();
    }


    public static void main(String[] args) {
        long start = System.currentTimeMillis();
        String tmp = "batteryPercentage";
        String s = preProcessingSingle(tmp);
        System.out.println(s);
        long end = System.currentTimeMillis();
        System.out.println(end - start);
    }
}
