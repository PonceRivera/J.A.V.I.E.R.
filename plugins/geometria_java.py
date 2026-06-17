
class Geometria {

    public static double calcularAreaCuadrado(double lado) {
        return lado * lado;
    }

    public static double calcularPerimetroCuadrado(double lado) {
        return 4 * lado;
    }

    public static double calcularAreaCirculo(double radio) {
        return Math.PI * radio * radio;
    }

    public static double calcularPerimetroCirculo(double radio) {
        return 2 * Math.PI * radio;
    }

    public static double calcularAreaTriangulo(double base, double altura) {
        return (base * altura) / 2;
    }

    public static double calcularPerimetroTrianguloEquilatero(double lado) {
        return 3 * lado;
    }

    public static void main(String[] args) {
        // Ejemplo de uso
        double ladoCuadrado = 5.0;
        System.out.println("Área del cuadrado de lado " + ladoCuadrado + ": " + calcularAreaCuadrado(ladoCuadrado));
        System.out.println("Perímetro del cuadrado de lado " + ladoCuadrado + ": " + calcularPerimetroCuadrado(ladoCuadrado));

        double radioCirculo = 3.0;
        System.out.println("Área del círculo de radio " + radioCirculo + ": " + calcularAreaCirculo(radioCirculo));
        System.out.println("Perímetro del círculo de radio " + radioCirculo + ": " + calcularPerimetroCirculo(radioCirculo));

        double baseTriangulo = 4.0;
        double alturaTriangulo = 6.0;
        System.out.println("Área del triángulo de base " + baseTriangulo + " y altura " + alturaTriangulo + ": " + calcularAreaTriangulo(baseTriangulo, alturaTriangulo));

        double ladoTrianguloEquilatero = 7.0;
        System.out.println("Perímetro del triángulo equilátero de lado " + ladoTrianguloEquilatero + ": " + calcularPerimetroTrianguloEquilatero(ladoTrianguloEquilatero));
    }
}
