package blstream.reports;

public class ReportGenerationException extends Exception {
	private static final long serialVersionUID = 1L;

	public ReportGenerationException(String message, Throwable e) {
		super(message, e);
	}
}
