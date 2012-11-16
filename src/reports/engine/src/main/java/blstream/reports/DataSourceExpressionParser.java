package blstream.reports;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class DataSourceExpressionParser {

	private String dataSourceExpression;

	public DataSourceExpressionParser(String dataSourceExpression) {
		this.dataSourceExpression = dataSourceExpression;
	}

	public String getUrl() {
		Pattern pattern = Pattern.compile("\"(http://[a-z0-9.:/_?=&]*)\"");

		Matcher m = pattern.matcher(dataSourceExpression);
		while (m.find()) {
			return m.group(1);
		}

		throw new IllegalStateException("Found no url in expression: " + dataSourceExpression);
	}

	public String replaceURLWith(String newUrl) {
		return dataSourceExpression.replace(getUrl(), newUrl);
	}
}
